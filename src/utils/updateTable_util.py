from pydantic import BaseModel

def updateTable(data : BaseModel | dict,models) :
    if isinstance(data,BaseModel) :
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(models, field, value)
    else :
        for field, value in data.items():
            if value is not None:
                setattr(models, field, value)