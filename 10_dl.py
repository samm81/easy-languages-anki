import youtube_dl


def main():
    ydl_opts = {format: "bestvideo[height<=360]+bestaudio/best[height<=480]"}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["https://www.youtube.com/watch?v=EuJlGjJSuKs"])


if __name__ == "__main__":
    main()
