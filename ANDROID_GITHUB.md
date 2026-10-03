# NOVA V11.1 — Android APK via GitHub Actions

1. Create a GitHub repository and upload the contents of this folder.
2. Push the files to the `main` branch.
3. Open **Actions**.
4. Select **Build NOVA Android APK**.
5. Press **Run workflow** if it has not started automatically.
6. Wait for the build to finish.
7. Open the successful run and scroll to **Artifacts**.
8. Download **NOVA-Android-APK** and extract the APK.

The APK asks for the Groq API key on first launch and stores it in Android's private application storage. The key is not included in this source package.
