from pydantic import BaseModel

class AddNotificationModel(BaseModel):
    id : int
    id_siswa : int | None = None
    id_guru_walas : int | None = None
    id_guru_mapel : int | None = None
    id_petugas_BK : int | None = None
    title : str
    body : str

