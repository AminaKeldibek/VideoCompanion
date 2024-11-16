I. Data Pipeline

Go to video_companion/video_content_search directory and run following to download audio in mp3 format and create
transcription as json

1. `poetry run python video_content_search/extract_audio.py https://www.youtube.com/watch?v=so9Iy2gtKyg&t=4120s -o
utput_path '../../data/'`

2. `poetry run python video_content_search/create_transcript.py "~/Projects/video_companion/data/audio/booking_event_small.mp3" -output_path="~/Projects/video_companion/data/transcription/booking_event_small.json"`

3.  `poetry run python video_content_search/add_documents.py ~/Projects/video_companion/data/transcription/booking_event.json`


II. Backend
1. Check that vector store is running from app in terminal

2. Start server use following command:
`poetry run uvicorn main:app --reload`

3. Test API
```
curl -X POST http://localhost:8000/search_video \
     -H "Content-Type: application/json" \
     -d '{
           "video_id": "111_xxx",
           "query": "комик из англии",
           "user_id": "Sunshine"
         }'
```


III. Front End
Front end create clickable Youtube URL for user
https://www.youtube.com/watch?v=gg6-NuwKnmQ&t=10
`https://www.youtube.com/watch?v=${data.video_id}&t=${data.timestamp}`;

IV. Integrate

Examples of search queries to try:
1. комик из англии
2. Персонажи из мультиков
3. мы не роботы
4. Wallet
5. Подарки