use tauri_plugin_deep_link::DeepLinkExt;

#[tauri::command]
fn pairing_token_flow_contract() -> &'static str {
    "central-api issues short-lived pairing token; desktop receives zhenzhi-ai-native://pair?token_ref=...; token secret stored through stronghold only after user confirms runner scope"
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_deep_link::init())
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            #[cfg(desktop)]
            {
                app.deep_link().register_all()?;
                app.handle()
                    .plugin(tauri_plugin_updater::Builder::new().build())?;

                let salt_path = app
                    .path()
                    .app_local_data_dir()
                    .expect("could not resolve app local data path")
                    .join("stronghold-salt.txt");
                app.handle().plugin(
                    tauri_plugin_stronghold::Builder::with_argon2(&salt_path).build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![pairing_token_flow_contract])
        .run(tauri::generate_context!())
        .expect("error while running zhenzhi ai native os desktop");
}
