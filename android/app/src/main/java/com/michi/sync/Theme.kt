package com.michi.sync

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF8FB7FF),
    secondary = Color(0xFF5A6A8A),
    tertiary = Color(0xFF34C759),
    background = Color(0xFF070A10),
    surface = Color(0xFF0D1018),
    surfaceVariant = Color(0xFF141822),
    onSurface = Color(0xFFD4D4D8),
    onSurfaceVariant = Color(0xFF71717A),
    outline = Color(0xFF3B3F47),
)

@Composable
fun MichiSyncTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        content = content,
    )
}
