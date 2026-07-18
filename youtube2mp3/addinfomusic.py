def addinfo(filename, info):
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.mp3 import MP3
    from mutagen import File
    import mimetypes
    import requests
    
    print(mimetypes.guess_type(filename))
    if isinstance(File(filename),MP3):
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCOM, COMM, APIC
        audio = MP3(filename, ID3=ID3)

        print(info.get("title"))
        # create tags if they don't exist
        if audio.tags is None:
            audio.add_tags()

        audio.tags.add(TPE1(encoding=3, text=info.get("channel", " ")))   # Artist
        audio.tags.add(TIT2(encoding=3, text=info.get("title", " ")))     # Title
        audio.tags.add(TALB(encoding=3, text=info.get("album", " ")))     # Album
        audio.tags.add(TCOM(encoding=3, text=info.get("uploader", " ")))  # Composer / uploader

        audio.tags.add(
            COMM(
                encoding=3,
                lang='eng',
                desc='description',
                text=info.get("description", " ")
            )
        )
        audio.tags.add(
    APIC(
        encoding=3,
        mime='image/jpeg',
        type=3,           # cover(front)
        desc='Cover',
        data=requests.get(info.get("thumbnail", " ")).content
    )
)
        print("Mp3")
    else:
        try: 
            audio = MP4(filename)
            audio['\xa9ART'] = info.get("channel") # '\xa9ART' is the tag for artist information
            audio['\xa9nam'] = info.get("title")
            audio['\xa9alb'] = info.get("album")
            audio['\xa9wrt'] = info.get("uploader")
            audio['desc'] = info.get("description")
            audio['covr'] = [MP4Cover(requests.get(info.get("thumbnail")).content, imageformat=MP4Cover.FORMAT_JPEG)]
        except Exception as e:
            print(e)
    audio.save()

#info={"channel":"test", "title":"Hello", "album":"test", "uploader":"person", "description":"description", "thumbnail":"test.png"}
#addinfo("/home/garfield/Desktop/youtuberemix/Halsey_-_Colors_pt._II_Audio.m4a", info)