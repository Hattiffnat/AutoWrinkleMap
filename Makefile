ADDON_ID=auto_wrinkle_map
EXTENSION_FOLDER=extension_release


build-extension-archive:
	mkdir -p $(EXTENSION_FOLDER)/$(ADDON_ID)
	cp $(ADDON_ID)/blender_manifest.toml $(ADDON_ID)/*.py $(EXTENSION_FOLDER)/$(ADDON_ID)/
	cp -r auto_wrinkle_map/icons $(EXTENSION_FOLDER)/$(ADDON_ID)/icons
	cd ./$(EXTENSION_FOLDER) &&	zip -r ./$(ADDON_ID)_extension.zip .

fmt:
	black .
	isort .
