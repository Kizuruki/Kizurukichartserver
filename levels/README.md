# Static Levels
In this folder, you can upload static levels.

Since there are no examples uploaded for you, this readme will be your guide to uploading here.

### Location
Level folders go `/levels/{engine_name}/{level_uuid}.zip` (generate a random uuid from some web source.)

Instead of defining a `levels.json`, the server will iterate all directories here instead, so no need for that.

### Files in a Level ZIP Folder
Before zipping, ensure the following:
1. `music.mp3`
2. `level.data` (THIS IS PROBABLY NOT A SUS FILE!!)
3. `music_pre.mp3` OPTIONAL
4. `jacket.png`
5. `stage.png` OPTIONAL - if not provided, one will be generated using `jacket.png`
6. `stage_thumbnail.png` OPTIONAL - must be provided if stage.png is provided (will also be generated from jacket.png)