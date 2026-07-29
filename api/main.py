from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(
    title="寒柳别苑 API",
    description="为 zylatent.com 提供的学习型接口",
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
    description="记录学习、制作与思考。",
    topics=["Python", "AI", "软件工程", "写作"],
)


class PostSummary(BaseModel):
    slug: str
    title: str
    category: str
    tags: list[str]


POSTS = [
    PostSummary(
        slug="fastapi-basics",
        title="FastAPI 入门：给寒柳别苑搭一个小型 API",
        category="尺蠖",
        tags=["Python", "FastAPI"],
    ),
    PostSummary(
        slug="cpp-memory-ownership-raii",
        title="谁拥有这块内存：一次 C++ 资源管理实验",
        category="尺蠖",
        tags=["C++", "内存管理"],
    ),
]


class PostDetail(PostSummary):
    content: str


POST_CONTENT = {
    "fastapi-basics": "这是一篇 FastAPI 学习记录。",
    "cpp-memory-ownership-raii": "这是一篇 C++ 内存管理学习记录。",
}


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
    summary = next((post for post in POSTS if post.slug == slug), None)
    if summary is None:
        raise HTTPException(status_code=404, detail="文章不存在")

    return PostDetail(
        **summary.model_dump(),
        content=POST_CONTENT.get(slug, ""),
    )


@app.post("/api/feedback", response_model=FeedbackOut, status_code=201, tags=["feedback"])
def create_feedback(payload: FeedbackCreate):
    feedback = FeedbackOut(
        id=len(FEEDBACKS) + 1,
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    FEEDBACKS.append(feedback)
    return feedback
