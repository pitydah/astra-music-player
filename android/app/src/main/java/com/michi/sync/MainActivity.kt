/**
 * Michi Sync — Android test client.
 * Minimal proof-of-concept for the Michi Sync Suite protocol.
 */
package com.michi.sync

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val deviceIdentity = DeviceIdentity(this)
        val apiClient = ApiClient()

        setContent {
            MichiSyncTheme {
                SyncScreen(deviceIdentity, apiClient)
            }
        }
    }
}

@Composable
fun SyncScreen(deviceIdentity: DeviceIdentity, apiClient: ApiClient) {
    var ip by remember { mutableStateOf("192.168.1.") }
    var port by remember { mutableStateOf("53318") }
    var statusText by remember { mutableStateOf("Listo") }
    var sessionToken by remember { mutableStateOf("") }
    var manifestInfo by remember { mutableStateOf("") }
    var downloadStatus by remember { mutableStateOf("") }

    val scope = rememberCoroutineScope()
    val baseUrl = "http://$ip:$port"

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text(
                "Michi Sync",
                fontSize = 28.sp,
                fontFamily = FontFamily.Monospace,
                color = MaterialTheme.colorScheme.primary,
            )
            Text(
                "Cliente Android de prueba",
                fontSize = 13.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            // ── Server config ──
            OutlinedTextField(
                value = ip,
                onValueChange = { ip = it },
                label = { Text("IP del servidor KDE") },
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = port,
                onValueChange = { port = it },
                label = { Text("Puerto") },
                modifier = Modifier.fillMaxWidth(),
            )

            Text(
                "Device ID: ${deviceIdentity.getId()}",
                fontSize = 11.sp,
                fontFamily = FontFamily.Monospace,
                color = MaterialTheme.colorScheme.outline,
            )

            // ── Actions ──
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Button(onClick = {
                    scope.launch {
                        statusText = "Registrando..."
                        val result = withContext(Dispatchers.IO) {
                            apiClient.register(
                                baseUrl, deviceIdentity.getId(),
                                "Xiaomi 15 Ultra", "Xiaomi 15 Ultra",
                            )
                        }
                        result.fold(
                            onSuccess = { resp ->
                                sessionToken = resp.sessionToken
                                statusText = "Registrado. " +
                                    "Server: ${resp.serverDeviceId.take(12)}... " +
                                    "Library: ${resp.librarySize} tracks"
                            },
                            onFailure = { e ->
                                statusText = "Error: ${e.message}"
                            },
                        )
                    }
                }) { Text("Registrar") }

                Button(onClick = {
                    scope.launch {
                        if (sessionToken.isEmpty()) {
                            statusText = "Regístrate primero"
                            return@launch
                        }
                        statusText = "Obteniendo manifiesto..."
                        val result = withContext(Dispatchers.IO) {
                            apiClient.getManifest(
                                baseUrl, sessionToken,
                                deviceIdentity.getId(),
                            )
                        }
                        result.fold(
                            onSuccess = { m ->
                                manifestInfo =
                                    "${m.tracks} canciones — ${"%.1f".format(m.sizeMB)} MB"
                                statusText = "Manifiesto listo"
                            },
                            onFailure = { e ->
                                statusText = "Error: ${e.message}"
                            },
                        )
                    }
                }) { Text("Manifiesto") }

                Button(onClick = {
                    scope.launch {
                        if (sessionToken.isEmpty()) {
                            statusText = "Regístrate primero"
                            return@launch
                        }
                        statusText = "Descargando..."
                        val result = withContext(Dispatchers.IO) {
                            apiClient.downloadFirstTrack(
                                baseUrl, sessionToken,
                                deviceIdentity.getId(),
                                filesDir,
                            )
                        }
                        result.fold(
                            onSuccess = { info ->
                                downloadStatus = info
                                statusText = "Descarga OK"
                            },
                            onFailure = { e ->
                                downloadStatus = ""
                                statusText = "Error: ${e.message}"
                            },
                        )
                    }
                }) { Text("Descargar 1") }
            }

            // ── Status ──
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant,
                ),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Estado: $statusText",
                        fontSize = 14.sp,
                        fontFamily = FontFamily.Monospace,
                    )
                    if (manifestInfo.isNotEmpty()) {
                        Text(
                            manifestInfo,
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.primary,
                        )
                    }
                    if (sessionToken.isNotEmpty()) {
                        Text(
                            "Token: ${sessionToken.take(20)}...",
                            fontSize = 10.sp,
                            fontFamily = FontFamily.Monospace,
                            color = MaterialTheme.colorScheme.outline,
                        )
                    }
                    if (downloadStatus.isNotEmpty()) {
                        Text(
                            downloadStatus,
                            fontSize = 11.sp,
                            fontFamily = FontFamily.Monospace,
                            color = MaterialTheme.colorScheme.tertiary,
                        )
                    }
                }
            }
        }
    }
}
