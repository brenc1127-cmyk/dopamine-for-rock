%define _enable_debug_packages %{nil}
%define debug_package %{nil}

Name:           dopamine
Version:        3.0.8
Release:        1
Summary:        An audio player that keeps it simple
License:        MIT
Group:          Sound
URL:            https://github.com/digimezzo/dopamine
Source0:        https://github.com%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        dopamine-node_modules-%{version}.tar.gz

BuildRequires:  nodejs
BuildRequires:  npm
# Add OpenMandriva's native typescript compiler package
BuildRequires:  typescript

%description
Dopamine is an elegant Electron audio player.

%prep
# Standard setup macro: -a 1 tells it to automatically unpack Source1 into the same directory
%setup -q -n %{name}-%{version} -a 1

%build
# 1. Expand Node's maximum RAM usage footprint to 4GB to stop the container freeze
export NODE_OPTIONS="--max-old-space-size=4096"

# 2. Re-assert path scopes inside your active folder path
export PATH="$(pwd)/node_modules/.bin:/usr/bin:$PATH"
export ELECTRON_SKIP_BINARY_DOWNLOAD=1

# 3. Clean compile the TypeScript configuration
npx tsc -p tsconfig-serve.json

# 4. Force electron-builder to pack purely without triggering deep dependency audits
./node_modules/.bin/electron-builder --linux --dir --config.asar=true

%install
# 1. Initialize fresh deployment target folders inside the container
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/dopamine
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps

# 2. Extract the compiled Electron output directory assets
cp -r dist/linux-unpacked/* %{buildroot}/opt/dopamine/

# 3. Clean up zero-length files to guarantee a silent rpmlint scan
find %{buildroot}/opt/dopamine/ -type f -size 0 -name "*.scss" -delete
find %{buildroot}/opt/dopamine/ -type f -name ".gitkeep" -delete

# 4. Generate the persistent runtime symbolic link for user shell launches
ln -rs %{buildroot}/opt/dopamine/Dopamine %{buildroot}%{_bindir}/dopamine

# 5. Automatically write out your customized desktop entry file on the fly
cat << 'EOF' > %{buildroot}%{_datadir}/applications/dopamine.desktop
[Desktop Entry]
Name=Dopamine
Comment=Elegant Native Audio Player
Exec=dopamine --no-sandbox --audio-buffer-size=2048
Terminal=false
Type=Application
Icon=dopamine
StartupWMClass=dopamine
Categories=AudioVideo;Audio;Player;
MimeType=audio/mpeg;audio/x-mpegurl;audio/x-scpls;
EOF

# 6. Copy the high-res 256x256 image asset to register the system shortcut icon
cp build/icons/256x256.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/dopamine.png


%files
/opt/dopamine/
%{_bindir}/dopamine
%{_datadir}/applications/dopamine.desktop
%{_datadir}/icons/hicolor/256x256/apps/dopamine.png
