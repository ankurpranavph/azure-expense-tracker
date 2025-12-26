from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field


import models
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1)
    amount: float = Field(gt=0)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Azure Expense Tracker is running 🚀"}

@app.post("/add-expense")
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    new_expense = models.Expense(
        title=expense.title,
        amount=expense.amount
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@app.get("/expenses")
def get_expenses(db: Session = Depends(get_db)):
    return db.query(models.Expense).all()
@app.delete("/delete-expense/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        return {"error": "Expense not found"}
    db.delete(expense)
    db.commit()
    return {"status": "Expense deleted"}

