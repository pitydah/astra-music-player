/**
 * HTTP API client for Michi Sync Suite.
 * Handles register, manifest, and download.
 */
package com.michi.sync

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.File
import java.security.MessageDigest

class ApiClient {
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .build()

    private val JSON = "application/json; charset=utf-8".toMediaType()

    data class RegisterResult(
        val sessionToken: String,
        val serverDeviceId: String,
        val clientDeviceId: String,
        val librarySize: Int,
    )

    data class ManifestResult(
        val tracks: Int,
        val sizeMB: Float,
        val firstTrack: TrackInfo?,
    )

    data class TrackInfo(
        val trackId: String,
        val title: String,
        val artist: String,
        val downloadPath: String,
        val checksum: String,
    )

    fun register(
        baseUrl: String, clientDeviceId: String,
        alias: String, deviceModel: String,
    ): Result<RegisterResult> = runCatching {
        val json = JSONObject().apply {
            put("alias", alias)
            put("device", "android")
            put("device_model", deviceModel)
            put("client_device_id", clientDeviceId)
        }
        val body = json.toString().toRequestBody(JSON)
        val request = Request.Builder()
            .url("$baseUrl/api/register")
            .post(body)
            .build()

        val response = client.newCall(request).execute()
        if (!response.isSuccessful) {
            throw Exception("Register failed: ${response.code}")
        }
        val data = JSONObject(response.body!!.string())
        RegisterResult(
            sessionToken = data.getString("session_token"),
            serverDeviceId = data.getString("server_device_id"),
            clientDeviceId = data.getString("client_device_id"),
            librarySize = data.getInt("library_size"),
        )
    }

    fun getManifest(
        baseUrl: String, token: String, deviceId: String,
    ): Result<ManifestResult> = runCatching {
        val request = Request.Builder()
            .url("$baseUrl/api/sync/manifest?device_id=$deviceId")
            .header("Authorization", "Bearer $token")
            .get()
            .build()

        val response = client.newCall(request).execute()
        if (!response.isSuccessful) {
            throw Exception("Manifest failed: ${response.code}")
        }
        val data = JSONObject(response.body!!.string())
        val tracks = data.getJSONArray("tracks")
        val totalSize = data.getLong("total_size")
        var first: TrackInfo? = null
        if (tracks.length() > 0) {
            val t = tracks.getJSONObject(0)
            first = TrackInfo(
                trackId = t.getString("track_id"),
                title = t.getString("title"),
                artist = t.getString("artist"),
                downloadPath = t.getString("download_path"),
                checksum = t.getString("checksum"),
            )
        }
        ManifestResult(
            tracks = data.getInt("total_tracks"),
            sizeMB = totalSize / (1024.0 * 1024.0).toFloat(),
            firstTrack = first,
        )
    }

    fun downloadFirstTrack(
        baseUrl: String, token: String, deviceId: String,
        outputDir: File,
    ): Result<String> = runCatching {
        val manifest = getManifest(baseUrl, token, deviceId).getOrThrow()
        val track = manifest.firstTrack
            ?: throw Exception("No tracks in manifest")

        val request = Request.Builder()
            .url("$baseUrl${track.downloadPath}")
            .header("Authorization", "Bearer $token")
            .get()
            .build()

        val response = client.newCall(request).execute()
        if (!response.isSuccessful) {
            throw Exception("Download failed: ${response.code}")
        }

        val bytes = response.body!!.bytes()
        val actualHash = MessageDigest.getInstance("SHA-256")
            .digest(bytes).joinToString("") { "%02x".format(it) }

        if (actualHash != track.checksum) {
            throw Exception(
                "Checksum mismatch!\nExpected: ${track.checksum.take(16)}\n" +
                "Got: ${actualHash.take(16)}"
            )
        }

        val file = File(outputDir, "${track.trackId}.${track.title.replace(" ", "_")}")
        file.outputStream().use { it.write(bytes) }

        "OK — ${track.title} · ${track.artist} · " +
            "${"%.2f".format(bytes.size / 1048576.0)} MB · SHA256 ✓"
    }
}
