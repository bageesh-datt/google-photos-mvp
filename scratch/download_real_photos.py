import os
import urllib.request
from PIL import Image

os.makedirs("backend/app/data/photos", exist_ok=True)
os.makedirs("frontend/public/photos", exist_ok=True)

PHOTO_URLS = {
    "P001": "https://images.unsplash.com/photo-1605826832916-d0ea9d6fe71e?w=800&q=80",
    "P002": "https://images.unsplash.com/photo-1577717903315-1691ae25ab3f?w=800&q=80",
    "P003": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=800&q=80",
    "P004": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80",
    "P005": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=800&q=80",
    "P006": "https://images.unsplash.com/photo-1584441405886-bc91be61e56a?w=800&q=80",
    "P007": "https://images.unsplash.com/photo-1512389142860-9c449e58a543?w=800&q=80",
    "P008": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&q=80",
    "P009": "https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=800&q=80",
    "P010": "https://images.unsplash.com/photo-1609234656388-0ff363383899?w=800&q=80",
    "P011": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",
    "P012": "https://images.unsplash.com/photo-1519741497674-611481863552?w=800&q=80",
    "P013": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?w=800&q=80",
    "P014": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80",
    "P015": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800&q=80",
    "P016": "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=800&q=80",
    "P017": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&q=80",
    "P018": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&q=80",
    "P019": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&q=80",
    "P020": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800&q=80",
    "P021": "https://images.unsplash.com/photo-1558636508-e0db3814bd1d?w=800&q=80",
    "P022": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&q=80",
    "P023": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",
    "P024": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=800&q=80",
    "P025": "https://images.unsplash.com/photo-1583939003579-730e3918a45a?w=800&q=80",
    "P026": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=800&q=80",
    "P027": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80",
    "P028": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80",
    "P029": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=800&q=80",
    "P030": "https://images.unsplash.com/photo-1554415707-6e8cfc93fe23?w=800&q=80",
    "P031": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=800&q=80",
    "P032": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&q=80",
    "P033": "https://images.unsplash.com/photo-1563720223185-11003d516935?w=800&q=80",
    "P034": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=800&q=80",
    "P035": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=80",
    "P036": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&q=80",
    "P037": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=800&q=80",
    "P038": "https://images.unsplash.com/photo-1614027164847-1b28cfe1df60?w=800&q=80",

    "P039": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&q=80",
    "P040": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=800&q=80",
    "P041": "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=800&q=80",
    "P042": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800&q=80",
    "P043": "https://images.unsplash.com/photo-1520763185298-1b434c919102?w=800&q=80",
    "P044": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800&q=80",
    "P045": "https://images.unsplash.com/photo-1604999565976-8913ad2ddb7c?w=800&q=80",
    "P046": "https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80",
    "P047": "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=800&q=80",
    "P048": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800&q=80",
    "P049": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=800&q=80",
    "P050": "https://images.unsplash.com/photo-1530866495561-507c9faab2ed?w=800&q=80"
}

def main():
    print("Downloading 50 real photographic images from Unsplash...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    for pid, url in PHOTO_URLS.items():
        filename = f"{pid}.jpg"
        p1 = os.path.join("backend/app/data/photos", filename)
        p2 = os.path.join("frontend/public/photos", filename)
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp, open(p1, 'wb') as out_file:
                out_file.write(resp.read())
                
            with Image.open(p1) as img:
                img.convert('RGB').save(p2, 'JPEG', quality=90)
                
            print(f"SUCCESS {pid}.jpg ({img.size[0]}x{img.size[1]})")
        except Exception as e:
            print(f"ERROR {pid}: {e}")
            
    print("\nAll 50 real photos processed!")

if __name__ == "__main__":
    main()
