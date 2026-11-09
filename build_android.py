#!/usr/bin/env python3
# Builds a small Android project (a WebView holding the app files) into ./android-build
# It is run by GitHub Actions; the APK always contains the current index.html.
import base64, os, re, shutil, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'android-build')
PKG = 'app.trexkon.calc'
KEYSTORE = """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
m1w5RqTBN5oCAicQ"""


def put(rel, text):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)


def embed_fonts(html, assets):
    """Download the Google Fonts files once at build time so the APK shows the same fonts offline."""
    m = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com/css2[^"]+)">', html)
    if not m:
        return html
    try:
        ua = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36'}
        css = urllib.request.urlopen(urllib.request.Request(m.group(1), headers=ua), timeout=30).read().decode('utf-8')
        urls = sorted(set(re.findall(r'url\((https://[^)]+)\)', css)))
        if not urls:
            raise RuntimeError('no font files found')
        os.makedirs(os.path.join(assets, 'fonts'), exist_ok=True)
        for i, u in enumerate(urls):
            name = 'f%d.woff2' % i
            data = urllib.request.urlopen(urllib.request.Request(u, headers=ua), timeout=30).read()
            with open(os.path.join(assets, 'fonts', name), 'wb') as f:
                f.write(data)
            css = css.replace(u, 'fonts/' + name)
        print('fonts embedded:', len(urls))
        return html.replace(m.group(0), '<style>' + css + '</style>')
    except Exception as e:
        print('fonts skipped, system fonts will be used:', e)
        return html


SETTINGS = """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = 'TrexKon'
include ':app'
"""

ROOT_GRADLE = """plugins {
    id 'com.android.application' version '8.5.2' apply false
}
"""

PROPS = """android.useAndroidX=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
"""

APP_GRADLE = """plugins {
    id 'com.android.application'
}

android {
    namespace '__PKG__'
    compileSdk 34

    defaultConfig {
        applicationId '__PKG__'
        minSdk 21
        targetSdk 34
        versionCode Integer.parseInt(System.getenv('GITHUB_RUN_NUMBER') ?: '1')
        versionName '1.0'
    }

    signingConfigs {
        release {
            storeFile file('release.jks')
            storePassword 'trexkon'
            keyAlias 'trexkon'
            keyPassword 'trexkon'
        }
    }

    buildTypes {
        release {
            minifyEnabled false
            signingConfig signingConfigs.release
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }

    lint {
        abortOnError false
        checkReleaseBuilds false
    }
}

dependencies {
    implementation 'androidx.webkit:webkit:1.11.0'
}
"""

MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="تركس وكونكان"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.DeviceDefault.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|screenLayout|keyboardHidden|smallestScreenSize|uiMode|density|layoutDirection"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

ACTIVITY = """package __PKG__;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.webkit.ValueCallback;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.webkit.WebViewAssetLoader;

public class MainActivity extends Activity {
    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.parseColor("#0A0B0C"));
        getWindow().setNavigationBarColor(Color.parseColor("#0A0B0C"));

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0A0B0C"));
        setContentView(web);

        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setUserAgentString(s.getUserAgentString() + " TrexKonApp");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }
        });

        if (state != null) {
            web.restoreState(state);
        } else {
            web.loadUrl("https://appassets.androidplatform.net/assets/index.html");
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    public void onBackPressed() {
        web.evaluateJavascript("window.appBack ? window.appBack() : false", new ValueCallback<String>() {
            @Override
            public void onReceiveValue(String value) {
                if (!"true".equals(value)) {
                    finish();
                }
            }
        });
    }
}
"""


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    app = os.path.join(OUT, 'app')
    main_dir = os.path.join(app, 'src', 'main')
    assets = os.path.join(main_dir, 'assets')
    os.makedirs(assets)

    with open(os.path.join(ROOT, 'index.html'), encoding='utf-8') as f:
        html = f.read()
    html = embed_fonts(html, assets)
    with open(os.path.join(assets, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    shutil.copy(os.path.join(ROOT, 'icon-192.png'), os.path.join(assets, 'icon-192.png'))

    mip = os.path.join(main_dir, 'res', 'mipmap-xxxhdpi')
    os.makedirs(mip)
    shutil.copy(os.path.join(ROOT, 'icon-192.png'), os.path.join(mip, 'ic_launcher.png'))

    with open(os.path.join(app, 'release.jks'), 'wb') as f:
        f.write(base64.b64decode(KEYSTORE))

    put('settings.gradle', SETTINGS)
    put('build.gradle', ROOT_GRADLE)
    put('gradle.properties', PROPS)
    put('app/build.gradle', APP_GRADLE.replace('__PKG__', PKG))
    put('app/src/main/AndroidManifest.xml', MANIFEST)
    put('app/src/main/java/' + PKG.replace('.', '/') + '/MainActivity.java', ACTIVITY.replace('__PKG__', PKG))
    print('android project ready in', OUT)


if __name__ == '__main__':
    main()
