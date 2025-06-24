ADDON_ID=auto_wrinkle_map
EXTENSIONS_PATH=~/.config/blender/4.4/extensions/user_default
ADDON_PATH=$(EXTENSIONS_PATH)/$(ADDON_ID)

RELEASE_FOLDER=extension_release
RELEASE_PATH=$(RELEASE_FOLDER)/$(ADDON_ID)

TEST_FILE=blend/wrinkle_test.blend
# TEST_FILE=blend/empty_file.blend

build-extension-archive:
	rm -rf $(RELEASE_PATH)
	mkdir -p $(RELEASE_PATH)
	cp $(ADDON_ID)/blender_manifest.toml $(ADDON_ID)/*.py $(RELEASE_PATH)/
	cp -r $(ADDON_ID)/icons $(RELEASE_PATH)/icons
	cd ./$(RELEASE_FOLDER) && zip -ru ./$(ADDON_ID)_extension.zip .

run-in-blender:
	make build-extension-archive
	rm -rf $(ADDON_PATH)
	cp -r $(RELEASE_PATH) $(EXTENSIONS_PATH)

	/usr/bin/blender $(TEST_FILE) --addons $(ADDON_ID)


fmt:
	ruff format .
	isort .
