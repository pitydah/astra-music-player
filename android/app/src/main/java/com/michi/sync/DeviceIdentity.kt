/**
 * Persistent device identity using SharedPreferences.
 * Generates a stable UUID on first launch.
 */
package com.michi.sync

import android.content.Context

class DeviceIdentity(context: Context) {
    private val prefs = context.getSharedPreferences("michi_sync", Context.MODE_PRIVATE)

    fun getId(): String {
        var id = prefs.getString("client_device_id", null)
        if (id == null) {
            id = "android_${java.util.UUID.randomUUID()}"
            prefs.edit().putString("client_device_id", id).apply()
        }
        return id
    }
}
