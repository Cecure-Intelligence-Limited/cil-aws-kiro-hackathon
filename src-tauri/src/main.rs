// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{
    AppHandle, CustomMenuItem, GlobalShortcutManager, Manager, SystemTray, SystemTrayEvent,
    SystemTrayMenu, SystemTrayMenuItem, Window, WindowEvent,
};

// System tray menu items
fn create_system_tray() -> SystemTray {
    let quit = CustomMenuItem::new("quit".to_string(), "Quit Aura");
    let show = CustomMenuItem::new("show".to_string(), "Show Assistant");
    let hide = CustomMenuItem::new("hide".to_string(), "Hide Assistant");
    let settings = CustomMenuItem::new("settings".to_string(), "Settings");
    
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(settings)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);
    
    SystemTray::new().with_menu(tray_menu)
}

// Handle system tray events
fn handle_system_tray_event(app: &AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::LeftClick {
            position: _,
            size: _,
            ..
        } => {
            let window = app.get_window("main").unwrap();
            if window.is_visible().unwrap() {
                window.hide().unwrap();
            } else {
                window.show().unwrap();
                window.set_focus().unwrap();
            }
        }
        SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
            "quit" => {
                std::process::exit(0);
            }
            "show" => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            "hide" => {
                let window = app.get_window("main").unwrap();
                window.hide().unwrap();
            }
            "settings" => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
                // Emit event to show settings modal
                window.emit("show-settings", {}).unwrap();
            }
            _ => {}
        },
        _ => {}
    }
}

// Toggle window visibility
#[tauri::command]
fn toggle_window(window: Window) {
    if window.is_visible().unwrap() {
        window.hide().unwrap();
    } else {
        window.show().unwrap();
        window.set_focus().unwrap();
    }
}

// Show window
#[tauri::command]
fn show_window(window: Window) {
    window.show().unwrap();
    window.set_focus().unwrap();
}

// Hide window
#[tauri::command]
fn hide_window(window: Window) {
    window.hide().unwrap();
}

// Get system information
#[tauri::command]
fn get_system_info() -> serde_json::Value {
    serde_json::json!({
        "platform": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "version": env!("CARGO_PKG_VERSION"),
        "name": env!("CARGO_PKG_NAME")
    })
}

// Check if file exists
#[tauri::command]
fn file_exists(path: String) -> bool {
    std::path::Path::new(&path).exists()
}

// Get app data directory
#[tauri::command]
fn get_app_data_dir(app: AppHandle) -> Option<String> {
    app.path_resolver()
        .app_data_dir()
        .map(|path| path.to_string_lossy().to_string())
}

// Get documents directory
#[tauri::command]
fn get_documents_dir(app: AppHandle) -> Option<String> {
    app.path_resolver()
        .document_dir()
        .map(|path| path.to_string_lossy().to_string())
}

fn main() {
    tauri::Builder::default()
        .system_tray(create_system_tray())
        .on_system_tray_event(handle_system_tray_event)
        .invoke_handler(tauri::generate_handler![
            toggle_window,
            show_window,
            hide_window,
            get_system_info,
            file_exists,
            get_app_data_dir,
            get_documents_dir
        ])
        .setup(|app| {
            // Register global shortcut
            let mut shortcut_manager = app.global_shortcut_manager();
            
            // Register Ctrl+' (Ctrl+Quote) as the global shortcut
            shortcut_manager
                .register("CmdOrCtrl+'", {
                    let app_handle = app.handle();
                    move || {
                        let window = app_handle.get_window("main").unwrap();
                        if window.is_visible().unwrap() {
                            window.hide().unwrap();
                        } else {
                            window.show().unwrap();
                            window.set_focus().unwrap();
                        }
                    }
                })
                .unwrap_or_else(|err| {
                    eprintln!("Failed to register global shortcut: {}", err);
                });

            // Alternative shortcut: Ctrl+Shift+A
            shortcut_manager
                .register("CmdOrCtrl+Shift+A", {
                    let app_handle = app.handle();
                    move || {
                        let window = app_handle.get_window("main").unwrap();
                        if window.is_visible().unwrap() {
                            window.hide().unwrap();
                        } else {
                            window.show().unwrap();
                            window.set_focus().unwrap();
                        }
                    }
                })
                .unwrap_or_else(|err| {
                    eprintln!("Failed to register alternative global shortcut: {}", err);
                });

            // Set up window event handlers
            let window = app.get_window("main").unwrap();
            
            // Handle window events
            window.on_window_event(move |event| match event {
                WindowEvent::CloseRequested { api, .. } => {
                    // Prevent window from closing, hide it instead
                    api.prevent_close();
                    let window = api.window();
                    window.hide().unwrap();
                }
                WindowEvent::Focused(false) => {
                    // Optionally hide window when it loses focus
                    // Uncomment the next line if you want this behavior
                    // api.window().hide().unwrap();
                }
                _ => {}
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}