use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use std::sync::Arc;
use tokio::sync::broadcast;

pub const TARGET_SAMPLE_RATE: u32 = 16000;
pub const TARGET_CHUNK_SAMPLES: usize = 1280; // 80ms a 16kHz
pub const TARGET_CHUNK_BYTES: usize = TARGET_CHUNK_SAMPLES * 2; // 16-bit PCM

#[derive(Clone, Copy, Debug)]
pub struct VadConfig {
    pub rms_threshold: f32,
    pub zcr_min: f32,
    pub zcr_max: f32,
    pub hangover_frames: usize,
}

impl Default for VadConfig {
    fn default() -> Self {
        Self {
            rms_threshold: 0.015,
            zcr_min: 0.02,
            zcr_max: 0.55,
            hangover_frames: 6, // ~480ms de retención tras voz
        }
    }
}

pub struct VadProcessor {
    config: VadConfig,
    hangover_remaining: usize,
    pre_buffer: Option<Vec<i16>>,
}

impl VadProcessor {
    pub fn new(config: VadConfig) -> Self {
        Self {
            config,
            hangover_remaining: 0,
            pre_buffer: None,
        }
    }

    /// Calcula RMS (Root Mean Square) del cuadro normalizado a [-1.0, 1.0]
    pub fn calculate_rms(samples: &[i16]) -> f32 {
        if samples.is_empty() {
            return 0.0;
        }
        let sum_sq: f32 = samples
            .iter()
            .map(|&s| {
                let norm = s as f32 / 32768.0;
                norm * norm
            })
            .sum();
        (sum_sq / samples.len() as f32).sqrt()
    }

    /// Calcula la tasa de cruce por cero (Zero-Crossing Rate)
    pub fn calculate_zcr(samples: &[i16]) -> f32 {
        if samples.len() < 2 {
            return 0.0;
        }
        let mut crossings = 0;
        for i in 1..samples.len() {
            if (samples[i] >= 0 && samples[i - 1] < 0) || (samples[i] < 0 && samples[i - 1] >= 0) {
                crossings += 1;
            }
        }
        crossings as f32 / (samples.len() as f32 - 1.0)
    }

    /// Evalúa el cuadro con VAD matemático y retorna si contiene voz
    pub fn process_frame(&mut self, samples: &[i16]) -> (bool, Option<Vec<i16>>) {
        let rms = Self::calculate_rms(samples);
        let zcr = Self::calculate_zcr(samples);

        let is_voice = rms >= self.config.rms_threshold
            && zcr >= self.config.zcr_min
            && zcr <= self.config.zcr_max;

        let mut emit_pre_buffer = None;

        if is_voice {
            if self.hangover_remaining == 0 && self.pre_buffer.is_some() {
                emit_pre_buffer = self.pre_buffer.take();
            }
            self.hangover_remaining = self.config.hangover_frames;
        } else if self.hangover_remaining > 0 {
            self.hangover_remaining -= 1;
        } else {
            // Guardar último cuadro de silencio para no cortar inicios abruptos de palabras
            self.pre_buffer = Some(samples.to_vec());
        }

        let is_active = is_voice || self.hangover_remaining > 0;
        (is_active, emit_pre_buffer)
    }
}

/// Convertidor de canales a mono y remuestreador lineal a 16kHz
pub struct AudioResampler {
    source_rate: u32,
    channels: usize,
    buffer_mono: Vec<f32>,
    resampled_samples: Vec<i16>,
    phase: f64,
}

impl AudioResampler {
    pub fn new(source_rate: u32, channels: usize) -> Self {
        Self {
            source_rate,
            channels,
            buffer_mono: Vec::new(),
            resampled_samples: Vec::new(),
            phase: 0.0,
        }
    }

    /// Procesa muestras entrantes intercaladas y produce muestras a 16kHz en `resampled_samples`
    pub fn process_interleaved_f32(&mut self, input: &[f32]) {
        // 1. Promediar canales a mono
        if self.channels > 1 {
            let frames = input.len() / self.channels;
            for i in 0..frames {
                let mut sum = 0.0;
                for c in 0..self.channels {
                    sum += input[i * self.channels + c];
                }
                self.buffer_mono.push(sum / self.channels as f32);
            }
        } else {
            self.buffer_mono.extend_from_slice(input);
        }

        // 2. Remuestreo lineal a 16kHz
        let ratio = self.source_rate as f64 / TARGET_SAMPLE_RATE as f64;
        let mut idx = self.phase;

        while (idx as usize) + 1 < self.buffer_mono.len() {
            let i = idx as usize;
            let frac = (idx - i as f64) as f32;
            let sample_f32 = self.buffer_mono[i] * (1.0 - frac) + self.buffer_mono[i + 1] * frac;
            let sample_i16 = (sample_f32.clamp(-1.0, 1.0) * 32767.0) as i16;
            self.resampled_samples.push(sample_i16);
            idx += ratio;
        }

        let consumed = idx as usize;
        self.phase = idx - consumed as f64;
        self.buffer_mono.drain(0..consumed);
    }

    pub fn take_resampled(&mut self) -> Vec<i16> {
        std::mem::take(&mut self.resampled_samples)
    }
}

/// Inicia la captura de audio en un hilo en segundo plano con CPAL
pub fn start_audio_capture(
    sender: broadcast::Sender<Vec<u8>>,
    config: VadConfig,
) -> Result<cpal::Stream, Box<dyn std::error::Error + Send + Sync>> {
    let host = cpal::default_host();
    let device = host
        .default_input_device()
        .ok_or("No se encontró dispositivo de entrada de audio")?;

    let device_name = device.name().unwrap_or_else(|_| "Desconocido".to_string());
    println!("Dispositivo de micrófono detectado: {}", device_name);

    let supported_config = device.default_input_config()?;
    let sample_rate = supported_config.sample_rate().0;
    let channels = supported_config.channels() as usize;
    let sample_format = supported_config.sample_format();

    println!(
        "Configuración de captura: {} Hz, {} canal(es), formato {:?}",
        sample_rate, channels, sample_format
    );

    let resampler = Arc::new(std::sync::Mutex::new(AudioResampler::new(
        sample_rate,
        channels,
    )));
    let vad = Arc::new(std::sync::Mutex::new(VadProcessor::new(config)));
    let accumulator = Arc::new(std::sync::Mutex::new(Vec::<i16>::with_capacity(
        TARGET_CHUNK_SAMPLES * 2,
    )));

    let sender_clone = sender.clone();
    let err_fn = |err| eprintln!("Error en stream de audio cpal: {}", err);

    let process_samples_f32 = {
        let resampler = Arc::clone(&resampler);
        let vad = Arc::clone(&vad);
        let accumulator = Arc::clone(&accumulator);
        let sender = sender_clone;

        move |raw_samples: &[f32]| {
            let mut resampler_lock = match resampler.lock() {
                Ok(g) => g,
                Err(_) => return,
            };
            resampler_lock.process_interleaved_f32(raw_samples);
            let samples = resampler_lock.take_resampled();
            drop(resampler_lock);

            if samples.is_empty() {
                return;
            }

            let mut acc_lock = match accumulator.lock() {
                Ok(g) => g,
                Err(_) => return,
            };
            acc_lock.extend_from_slice(&samples);

            let mut vad_lock = match vad.lock() {
                Ok(g) => g,
                Err(_) => return,
            };

            while acc_lock.len() >= TARGET_CHUNK_SAMPLES {
                let chunk: Vec<i16> = acc_lock.drain(0..TARGET_CHUNK_SAMPLES).collect();
                let (is_active, pre_buffer) = vad_lock.process_frame(&chunk);

                if is_active {
                    // Si había un pre-buffer guardado, enviarlo primero
                    if let Some(pre) = pre_buffer {
                        let mut bytes = Vec::with_capacity(TARGET_CHUNK_BYTES);
                        for s in pre {
                            bytes.extend_from_slice(&s.to_le_bytes());
                        }
                        let _ = sender.send(bytes);
                    }

                    // Enviar cuadro actual de voz
                    let mut bytes = Vec::with_capacity(TARGET_CHUNK_BYTES);
                    for s in chunk {
                        bytes.extend_from_slice(&s.to_le_bytes());
                    }
                    let _ = sender.send(bytes);
                }
            }
        }
    };

    let stream = match sample_format {
        cpal::SampleFormat::F32 => {
            let proc = process_samples_f32;
            device.build_input_stream(
                &supported_config.into(),
                move |data: &[f32], _| proc(data),
                err_fn,
                None,
            )?
        }
        cpal::SampleFormat::I16 => {
            let proc = process_samples_f32;
            device.build_input_stream(
                &supported_config.into(),
                move |data: &[i16], _| {
                    let f32_data: Vec<f32> = data.iter().map(|&s| s as f32 / 32768.0).collect();
                    proc(&f32_data);
                },
                err_fn,
                None,
            )?
        }
        cpal::SampleFormat::U16 => {
            let proc = process_samples_f32;
            device.build_input_stream(
                &supported_config.into(),
                move |data: &[u16], _| {
                    let f32_data: Vec<f32> =
                        data.iter().map(|&s| (s as f32 - 32768.0) / 32768.0).collect();
                    proc(&f32_data);
                },
                err_fn,
                None,
            )?
        }
        _ => return Err("Formato de muestra no soportado por cpal".into()),
    };

    stream.play()?;
    println!("Flujo de captura de micrófono activado con éxito.");
    Ok(stream)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_rms_silence() {
        let silence = vec![0i16; 1280];
        let rms = VadProcessor::calculate_rms(&silence);
        assert_eq!(rms, 0.0);
    }

    #[test]
    fn test_calculate_rms_signal() {
        // Señal constante a media escala (16384 / 32768 = 0.5)
        let signal = vec![16384i16; 1280];
        let rms = VadProcessor::calculate_rms(&signal);
        assert!((rms - 0.5).abs() < 0.01);
    }

    #[test]
    fn test_calculate_zcr() {
        let silence = vec![0i16; 10];
        let zcr_zero = VadProcessor::calculate_zcr(&silence);
        assert_eq!(zcr_zero, 0.0);

        // Señal alternante con cruces máximos
        let alternating = vec![1000, -1000, 1000, -1000, 1000];
        let zcr_alt = VadProcessor::calculate_zcr(&alternating);
        assert_eq!(zcr_alt, 1.0);
    }

    #[test]
    fn test_vad_speech_detection() {
        let mut vad = VadProcessor::new(VadConfig::default());

        // 1. Cuadro de silencio
        let silence = vec![0i16; 1280];
        let (is_active, _) = vad.process_frame(&silence);
        assert!(!is_active);

        // 2. Cuadro con señal similar a voz (RMS ~0.1, ZCR dentro del rango)
        let mut speech = Vec::with_capacity(1280);
        for i in 0..1280 {
            let val = ((i as f32 * 0.1).sin() * 5000.0) as i16;
            speech.push(val);
        }
        let (is_active_speech, _) = vad.process_frame(&speech);
        assert!(is_active_speech);
    }

    #[test]
    fn test_resampler() {
        let mut resampler = AudioResampler::new(48000, 1);
        let input_48k = vec![0.5f32; 480]; // 10ms a 48kHz
        resampler.process_interleaved_f32(&input_48k);
        let output = resampler.take_resampled();
        // A 16kHz, 10ms deberían ser aproximadamente 160 muestras
        assert!((output.len() as i32 - 160).abs() <= 2);
    }
}

