mod audio_input;

use audio_input::{start_audio_capture, VadConfig};
use rodio::{Decoder, OutputStream, Sink};
use std::io::Cursor;
use std::sync::Arc;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;
use tokio::sync::broadcast;

#[tokio::main]
async fn main() {
    println!("Iniciando Abril Rust Exo-skeleton...");

    // 1. Inicializar salida de audio (Reproducción WAV - Rodio)
    let (_stream, stream_handle) =
        OutputStream::try_default().expect("No se encontró dispositivo de salida de audio");
    let sink = Arc::new(Sink::try_new(&stream_handle).expect("Error creando el Sink de audio"));

    // 2. Inicializar entrada de audio (Micrófono con VAD matemático - CPAL)
    let (audio_tx, _) = broadcast::channel::<Vec<u8>>(128);
    let vad_config = VadConfig::default();

    let _input_stream = match start_audio_capture(audio_tx.clone(), vad_config) {
        Ok(s) => {
            println!("Captura de audio con VAD matemático iniciada correctamente.");
            Some(s)
        }
        Err(e) => {
            eprintln!("Advertencia: No se pudo iniciar captura de micrófono: {}", e);
            None
        }
    };

    // 3. Servidor de Reproducción de Voz (TCP 9001 - Recibe WAV de Kokoro TTS)
    let playback_listener = TcpListener::bind("127.0.0.1:9001").await.unwrap();
    println!("Audio de salida listo. Escuchando peticiones WAV en 127.0.0.1:9001...");

    let sink_clone = Arc::clone(&sink);
    tokio::spawn(async move {
        loop {
            match playback_listener.accept().await {
                Ok((mut socket, _)) => {
                    let sink = Arc::clone(&sink_clone);

                    tokio::spawn(async move {
                        let mut buf = Vec::new();
                        if let Ok(_) = socket.read_to_end(&mut buf).await {
                            if buf.is_empty() {
                                return;
                            }

                            println!("Recibidos {} bytes de audio. Reproduciendo...", buf.len());

                            let cursor = Cursor::new(buf);
                            match Decoder::new(cursor) {
                                Ok(source) => {
                                    sink.append(source);
                                }
                                Err(e) => {
                                    println!("Error decodificando audio: {:?}", e);
                                }
                            }
                        }
                    });
                }
                Err(e) => println!("Error aceptando conexión en 9001: {:?}", e),
            }
        }
    });

    // 4. Servidor de Streaming de Micrófono (TCP 9002 - Envía PCM 16kHz a Python)
    let mic_listener = TcpListener::bind("127.0.0.1:9002").await.unwrap();
    println!("Stream de micrófono listo. Transmitiendo audio activo en 127.0.0.1:9002...");

    tokio::spawn(async move {
        loop {
            match mic_listener.accept().await {
                Ok((mut socket, addr)) => {
                    println!("Cliente conectado al stream de voz (9002): {}", addr);
                    let mut rx = audio_tx.subscribe();

                    tokio::spawn(async move {
                        loop {
                            match rx.recv().await {
                                Ok(chunk) => {
                                    if let Err(_) = socket.write_all(&chunk).await {
                                        break;
                                    }
                                }
                                Err(broadcast::error::RecvError::Lagged(missed)) => {
                                    eprintln!(
                                        "Aviso: Cliente 9002 retrasado, cuadros perdidos: {}",
                                        missed
                                    );
                                }
                                Err(broadcast::error::RecvError::Closed) => {
                                    break;
                                }
                            }
                        }
                        println!("Cliente desconectado del stream de voz (9002): {}", addr);
                    });
                }
                Err(e) => println!("Error aceptando conexión en 9002: {:?}", e),
            }
        }
    });

    // Mantener en ejecución hasta interrupción
    match tokio::signal::ctrl_c().await {
        Ok(()) => println!("\nApagando Abril Rust Exo-skeleton..."),
        Err(e) => eprintln!("Error esperando señal de apagado: {}", e),
    }
}
