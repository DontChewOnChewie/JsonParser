echo "Starting Installation : This may take a couple of minutes."
pip install matplotlib
pip install folium
python -m pip install --upgrade pip wheel setuptools
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
#pip install kivy.deps.gstreamer
#pip install kivy.deps.angle
python -m pip install kivy
pip install kivy-garden
garden install matplotlib
echo 'Installation Complete'