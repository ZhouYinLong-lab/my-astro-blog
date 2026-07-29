import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(
    title="寒柳别苑 API",
    description="记录学习、工作与思考。",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zylatent.com",
        "https://www.zylatent.com",
        "http://localhost:4321",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class SiteProfile(BaseModel):
    name: str
    domain: str
    description: str
    topics: list[str]


SITE_PROFILE = SiteProfile(
    name="寒柳别苑",
    domain="zylatent.com",
    description="记录学习、工作与思考。",
    topics=["Python", "C++", "Claude Code Skills", "诗歌", "写作"],
)


class PostSummary(BaseModel):
    slug: str
    title: str
    category: str
    tags: list[str]


class PostDetail(PostSummary):
    content: str


POSTS_FILE = Path(__file__).parent / "data" / "posts.json"


def load_posts() -> list[PostDetail]:
    """从 JSON 加载文章，新增文章时只需要维护这个文件。"""
    with POSTS_FILE.open(encoding="utf-8") as file:
        return [PostDetail.model_validate(item) for item in json.load(file)]


POSTS = load_posts()


class FeedbackCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    message: str = Field(min_length=1, max_length=1000)
    page: str = Field(default="/", pattern=r"^/")


class FeedbackOut(FeedbackCreate):
    id: int
    created_at: datetime


FEEDBACKS: list[FeedbackOut] = []


@app.get("/", tags=["system"])
def read_root():
    return {"message": "寒柳别苑 API 正在运行", "docs": "/docs"}


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


@app.get("/api/site", response_model=SiteProfile, tags=["site"])
def read_site_profile():
    return SITE_PROFILE


@app.get("/api/posts", response_model=list[PostSummary], tags=["posts"])
def list_posts(
    category: str | None = None,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    result = POSTS
    if category is not None:
        result = [post for post in result if post.category == category]
    return result[offset : offset + limit]


@app.get("/api/posts/{slug}", response_model=PostDetail, tags=["posts"])
def get_post(slug: str):
    post = next((post for post in POSTS if post.slug == slug), None)
    if post is None:
        raise HTTPException(status_code=404, detail="文章不存在")

    return post


@app.post("/api/feedback", response_model=FeedbackOut, status_code=201, tags=["feedback"])
def create_feedback(payload: FeedbackCreate):
    feedback = FeedbackOut(
        id=len(FEEDBACKS) + 1,
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    FEEDBACKS.append(feedback)
    return feedback
