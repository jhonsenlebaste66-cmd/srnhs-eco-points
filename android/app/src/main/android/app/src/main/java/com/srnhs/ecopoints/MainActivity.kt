
package com.srnhs.ecopoints

import android.Manifest
import android.app.Activity
import android.os.Bundle
import android.content.pm.PackageManager
import android.webkit.*
import android.view.View
import android.widget.Toast
import android.graphics.Bitmap
import android.os.Build

class MainActivity : Activity() {

    private lateinit var webView: WebView
    private var pendingRequest: PermissionRequest? = null

    private val website =
        "https://srnhs-eco-points.streamlit.app/"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        webView.setBackgroundColor(android.graphics.Color.WHITE)

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            loadsImagesAutomatically = true
            javaScriptCanOpenWindowsAutomatically = false
            setSupportMultipleWindows(false)
        }

        CookieManager.getInstance().apply {
            setAcceptCookie(true)
            setAcceptThirdPartyCookies(webView, true)
        }

        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(
                view: WebView?,
                url: String?,
                favicon: Bitmap?
            ) {
                super.onPageStarted(view, url, favicon)
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onPermissionRequest(
                request: PermissionRequest
            ) {
                runOnUiThread {
                    val allowedHost =
                        request.origin.host == "srnhs-eco-points.streamlit.app"

                    if (!allowedHost) {
                        request.deny()
                        return@runOnUiThread
                    }

                    val cameraResources = request.resources.filter {
                        it == PermissionRequest.RESOURCE_VIDEO_CAPTURE
                    }

                    if (cameraResources.isEmpty()) {
                        request.deny()
                        return@runOnUiThread
                    }

                    if (checkSelfPermission(Manifest.permission.CAMERA)
                        == PackageManager.PERMISSION_GRANTED
                    ) {
                        request.grant(cameraResources.toTypedArray())
                    } else {
                        pendingRequest = request
                        requestPermissions(
                            arrayOf(Manifest.permission.CAMERA),
                            100
                        )
                    }
                }
            }
        }

        setContentView(webView)
        webView.loadUrl(website)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(
            requestCode, permissions, grantResults
        )

        if (requestCode == 100) {
            val request = pendingRequest
            pendingRequest = null

            if (grantResults.isNotEmpty() &&
                grantResults[0] == PackageManager.PERMISSION_GRANTED
            ) {
                request?.grant(
                    arrayOf(PermissionRequest.RESOURCE_VIDEO_CAPTURE)
                )
            } else {
                request?.deny()
                Toast.makeText(
                    this,
                    "Camera permission is required for QR scanning.",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }

    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        if (::webView.isInitialized && webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
