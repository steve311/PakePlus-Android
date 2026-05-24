#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
白马咖啡店 - 自动打包工具
支持打包为 Android APK 和 Windows EXE
"""

import os
import sys
import shutil
import subprocess
import json
import zipfile
from pathlib import Path

class CoffeeAppPacker:
    def __init__(self, project_dir="."):
        self.project_dir = Path(project_dir).absolute()
        self.build_dir = self.project_dir / "build"
        self.output_dir = self.project_dir / "output"
        
    def check_requirements(self):
        """检查打包所需环境"""
        requirements = {
            "node": "node --version",
            "npm": "npm --version",
            "electron": "npx electron --version",
            "electron-builder": "npx electron-builder --version"
        }
        
        print("🔍 检查环境依赖...")
        for name, cmd in requirements.items():
            try:
                subprocess.run(cmd, shell=True, check=True, capture_output=True)
                print(f"   ✓ {name} 已安装")
            except:
                print(f"   ✗ {name} 未安装，请先安装")
                
    def build_electron_exe(self):
        """打包为Electron EXE"""
        print("\n🪟 开始打包 Windows EXE...")
        
        # 创建Electron配置
        electron_dir = self.build_dir / "electron"
        electron_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制所有web文件
        shutil.copytree(self.project_dir, electron_dir / "app", dirs_exist_ok=True)
        
        # 创建main.js
        main_js = '''const { app, BrowserWindow, shell } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webSecurity: false
        },
        icon: path.join(__dirname, 'icon.ico'),
        title: '白马咖啡店的前世今生',
        backgroundColor: '#fdf8f0'
    });
    
    mainWindow.loadFile(path.join(__dirname, 'app', 'index.html'));
    
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
'''
        
        with open(electron_dir / "main.js", "w", encoding="utf-8") as f:
            f.write(main_js)
            
        # 创建package.json
        package_json = {
            "name": "baima-coffee",
            "version": "1.0.0",
            "main": "main.js",
            "scripts": {
                "start": "electron .",
                "build": "electron-builder"
            },
            "build": {
                "appId": "com.baima.coffee",
                "productName": "白马咖啡店",
                "directories": {"output": "dist"},
                "win": {
                    "target": "nsis",
                    "icon": "app/icon.ico"
                },
                "nsis": {
                    "oneClick": False,
                    "allowToChangeInstallationDirectory": True,
                    "createDesktopShortcut": True
                },
                "files": [
                    "main.js",
                    "app/**/*"
                ]
            },
            "devDependencies": {
                "electron": "^28.0.0",
                "electron-builder": "^24.6.4"
            }
        }
        
        with open(electron_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)
            
        # 安装依赖并打包
        os.chdir(electron_dir)
        subprocess.run("npm install", shell=True)
        subprocess.run("npm run build", shell=True)
        
        # 复制生成的EXE
        exe_file = electron_dir / "dist" / "白马咖啡店 Setup.exe"
        if exe_file.exists():
            shutil.copy(exe_file, self.output_dir / "白马咖啡店_Setup.exe")
            print(f"✅ EXE打包成功: {self.output_dir / '白马咖啡店_Setup.exe'}")
        else:
            print("❌ EXE打包失败，请检查electron-builder配置")
            
    def build_apk_webview(self):
        """打包为简单Android APK (使用WebView)"""
        print("\n📱 开始打包 Android APK...")
        
        # 创建Android项目结构
        android_dir = self.build_dir / "android_app"
        android_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建简单的WebView Activity模板 (需要在Android Studio中编译)
        print("⚠️ 完整APK打包需要安装Android Studio")
        print("📖 详细步骤:")
        print("   1. 下载Android Studio")
        print("   2. 创建新项目 -> Empty Activity")
        print("   3. 将assets文件复制到 app/src/main/assets/")
        print("   4. 修改MainActivity加载本地HTML")
        print("   5. Build -> Build APK")
        
        # 生成asset打包文件
        asset_dir = android_dir / "app/src/main/assets"
        asset_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.project_dir, asset_dir, dirs_exist_ok=True)
        
        # 生成MainActivity代码模板
        activity_code = '''package com.baima.coffee;

import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private WebView webView;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        webView = findViewById(R.id.webView);
        webView.setWebViewClient(new WebViewClient());
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setAllowFileAccess(true);
        webView.getSettings().setAllowFileAccessFromFileURLs(true);
        webView.getSettings().setAllowUniversalAccessFromFileURLs(true);
        
        // 加载本地HTML
        webView.loadUrl("file:///android_asset/index.html");
    }
}
'''
        
        with open(android_dir / "MainActivity.java", "w", encoding="utf-8") as f:
            f.write(activity_code)
            
        print(f"✅ Android资源已准备: {asset_dir}")
        print("📦 请使用Android Studio打开项目并构建APK")
        
    def create_offline_zip(self):
        """创建离线打包文件"""
        print("\n📦 创建离线分发包...")
        
        zip_path = self.output_dir / "白马咖啡店_离线网页版.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(self.project_dir):
                for file in files:
                    if file.endswith(('.html', '.js', '.css', '.txt', '.jpg', '.png', '.json')):
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.project_dir)
                        zipf.write(file_path, arcname)
                        
        print(f"✅ 离线包已创建: {zip_path}")
        
    def run(self):
        """执行打包流程"""
        print("=" * 50)
        print("☕ 白马咖啡店 打包工具 v1.0")
        print("=" * 50)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建离线包
        self.create_offline_zip()
        
        # 打包选项
        print("\n请选择打包方式:")
        print("1. 打包为Windows EXE (Electron)")
        print("2. 准备Android APK资源")
        print("3. 全部打包")
        
        choice = input("\n请输入选项 (1/2/3): ").strip()
        
        if choice in ['1', '3']:
            self.check_requirements()
            self.build_electron_exe()
            
        if choice in ['2', '3']:
            self.build_apk_webview()
            
        print("\n🎉 打包完成!")
        print(f"📁 输出目录: {self.output_dir}")

if __name__ == "__main__":
    packer = CoffeeAppPacker()
    packer.run()