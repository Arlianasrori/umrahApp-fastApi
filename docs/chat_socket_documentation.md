# 📡 Socket.IO Connection Documentation

Dokumentasi ini menjelaskan event-event yang digunakan dalam koneksi `Socket.IO` untuk fitur chat.

## 🔌 Koneksi

Pastikan klien telah terhubung ke server menggunakan `Socket.IO` sebelum mengirim atau menerima event berikut.

---

## URL : http://localhost:2008/socket
## 📨 Events

### 1. `start_chat`

#### 📤 On Event
server mengirimkan event ini kepada client. client dapat memodifikasi list room yang ada dan menambahkan room baru sesuai dengan response yang diberikan (push new room).

#### 📥 Response
```json
{
  "room_id": int,
  "to_user_name": str,
  "to_user_id": str,
  "last_message": str,
  "last_message_time": datetime,
  "count_not_read_message": int,
}
```
coba buka tempat km render chat
---

### 2. `new_message`

#### 📤 On Event
server mengirimkan event ini kepada client. client dapat memodifikasi list message yang ada dan menambahkan message dalam sebuah room sesuai dengan response yang diberikan (push new message).

#### 📥 Response
```json
{
  "id" : int,
  "room_id" : int,
  "message" : str,
  "sender_id" : int,
  "receiver_id" : int,
  "id_package" : int,
  "is_read" : bool,
  "created_at" : datetime.utc ,
  "updated_at" : datetime.utc,
  "package": {
    "id": int,
    "name": str,
    "departure_date": date,
    "image": str,
    "category": "PackageCategoryEnum",
    "detail": str
  },
  "package_price": {
    "id": int,
    "package_type": "PackageTypeEnum",
    "room_type": "RoomTypeEnum",
    "price": float,
    "detail": str,
    "seat_count": int
  }
}
```

---

### 3. `update_message`

#### 📤 Emit
server mengirimkan event ini kepada client. client dapat memfilter list message yang ada lalu mengupdate messagenya dengan response tersebut(jika ingin lebih mudah, client bisa melakukan request all message ulang  saat event ini ketrigger)

#### 📥 Response
```json
{
  "id" : int,
  "room_id" : int,
  "message" : str,
  "sender_id" : int,
  "receiver_id" : int,
  "id_package" : int,
  "is_read" : bool,
  "created_at" : datetime.utc ,
  "updated_at" : datetime.utc,
}
```

---

### 4. `delete_message`

#### 📤 Emit
server mengirimkan event ini kepada client. client dapat memfilter list message yang ada lalu menghapus messagenya (jika ingin lebih mudah, client bisa melakukan request all message ulang  saat event ini ketrigger)

#### 📥 Response
```json
{
  "id" : int,
  "room_id" : int,
  "message" : str,
  "sender_id" : int,
  "receiver_id" : int,
  "id_package" : int,
  "is_read" : bool,
  "created_at" : datetime.utc ,
  "updated_at" : datetime.utc,
}
```

---

### 5. `new_media_message`

#### 📤 Emit
server mengirim pesan dalam bentuk media (gambar/file), client dapat memfilter message berdasarkan message_id yang ada pada response (jika ingin lebih mudah, client bisa melakukan request all message ulang  saat event ini ketrigger).

#### 📥 Response
```json
{
  "id": int,
  "type": "file.content_type",
  "url": str,
  "message_id": int
}
```

---

### 6. `read_message`

#### 📤 Emit
server menandai pesan sebagai sudah dibaca sehingga client dapat melakuakn update seluruh message pada list menjadi is_read : true (jika ingin lebih mudah, client bisa melakukan request all message ulang  saat event ini ketrigger)

#### 📥 Response
```json
{
  "room_id": int
}
```

---

## 📘 Penting

- Semua waktu (`datetime`)  bersifat utc (agar saat melakukan chatting waktu chat dapat sesuai dengan local time user masing - masing) clinet harus melakukan parsing kembali datetime kelocal time user masing - maing menggunkan fitur yang telah ada pada bahasa pemrograman client.
- Enum yang digunakan seperti `PackageCategoryEnum`, `PackageTypeEnum`, dan `RoomTypeEnum` dapat dilihat pada api docs.