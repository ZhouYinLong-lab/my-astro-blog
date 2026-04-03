import { initializeApp } from "firebase/app";
import {
  getAuth,
  onAuthStateChanged,
  signInAnonymously,
  signInWithCustomToken,
} from "firebase/auth";
import {
  addDoc,
  collection,
  getFirestore,
  onSnapshot,
  query,
  serverTimestamp,
} from "firebase/firestore";
import { useEffect, useState } from "react";

// --- Firebase 初始化 ---
let app, auth, db, appId;
try {
  const firebaseConfig = JSON.parse(
    typeof __firebase_config !== "undefined" ? __firebase_config : "{}",
  );
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
  db = getFirestore(app);
  appId = typeof __app_id !== "undefined" ? __app_id : "default-app-id";
} catch (error) {
  console.error("Firebase config error:", error);
}

/**
 * 核心组件：复古打字机风问卷墙 (Brutalist Style)
 */
export default function DossierArchive({
  title = "柳含知的问卷",
  subtitle = "抛弃碎片的争吵，留下关于人性的结构化思考。",
  questions = [],
  archiveId = "default_archive",
}) {
  const [user, setUser] = useState(null);
  const [answersFeed, setAnswersFeed] = useState([]);
  const [loadingDb, setLoadingDb] = useState(true);

  const [formData, setFormData] = useState(Array(questions.length).fill(""));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState({ type: "", text: "" });

  // 1. 初始化 Auth
  useEffect(() => {
    if (!auth) return;
    const initAuth = async () => {
      try {
        if (
          typeof __initial_auth_token !== "undefined" &&
          __initial_auth_token
        ) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) {
        console.error("Auth init failed:", err);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  // 2. 监听对应 archiveId 的数据
  useEffect(() => {
    if (!user || !db || !archiveId) return;

    const colRef = collection(
      db,
      "artifacts",
      appId,
      "public",
      "data",
      archiveId,
    );
    const q = query(colRef);

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const docs = snapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        }));

        docs.sort((a, b) => {
          const timeA = a.createdAt?.toMillis
            ? a.createdAt.toMillis()
            : a.createdAt || 0;
          const timeB = b.createdAt?.toMillis
            ? b.createdAt.toMillis()
            : b.createdAt || 0;
          return timeB - timeA;
        });

        setAnswersFeed(docs);
        setLoadingDb(false);
      },
      (error) => {
        console.error("Firestore fetch error:", error);
        setLoadingDb(false);
      },
    );

    return () => unsubscribe();
  }, [user, archiveId]);

  const handleInputChange = (index, value) => {
    const newData = [...formData];
    newData[index] = value;
    setFormData(newData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user || !db) {
      setSubmitMessage({ type: "error", text: "【！通信中断】请稍后再试。" });
      return;
    }

    const filledAnswers = formData
      .map((ans, idx) => ({
        qId: idx,
        question: questions[idx],
        answer: ans.trim(),
      }))
      .filter((item) => item.answer !== "");

    if (filledAnswers.length === 0) {
      setSubmitMessage({
        type: "error",
        text: "【！空白卷宗】请至少作答一问。",
      });
      return;
    }

    setIsSubmitting(true);
    setSubmitMessage({ type: "", text: "" });

    try {
      const colRef = collection(
        db,
        "artifacts",
        appId,
        "public",
        "data",
        archiveId,
      );
      await addDoc(colRef, {
        userId: user.uid,
        answers: filledAnswers,
        createdAt: serverTimestamp(),
      });

      setSubmitMessage({
        type: "success",
        text: "【√ 封存完毕】已刻录至底层档案。",
      });
      setFormData(Array(questions.length).fill(""));
      setTimeout(() => setSubmitMessage({ type: "", text: "" }), 3000);
    } catch (err) {
      setSubmitMessage({
        type: "error",
        text: `【！封装异常】${err.message}`,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // 一键下载 JSON
  const handleExportData = () => {
    if (answersFeed.length === 0) return;

    const exportData = answersFeed.map((feed) => ({
      agentId: `Agent_${feed.userId?.substring(0, 6)}`,
      submittedAt: formatTime(feed.createdAt),
      answers: feed.answers.map((a) => ({
        question: a.question,
        answer: a.answer,
      })),
    }));

    const dataStr = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(exportData, null, 2),
    )}`;
    const downloadAnchorNode = document.createElement("a");
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `${archiveId}_archive.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return "未知时空";
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="bg-[#fcfaf2] text-black font-mono p-4 md:p-8 border-4 border-black shadow-[8px_8px_0_0_#111] relative">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 border-b-4 border-black pb-4">
        <div>
          <h2 className="text-2xl md:text-4xl font-black tracking-widest mb-2 uppercase text-black">
            『 {title} 』
          </h2>
          <p className="font-bold text-sm bg-black text-white inline-block px-3 py-1.5 shadow-[2px_2px_0_0_#ffcc00]">
            {subtitle}
          </p>
        </div>

        <button
          type="button"
          onClick={handleExportData}
          disabled={answersFeed.length === 0}
          className="mt-4 md:mt-0 flex items-center gap-2 bg-[#88cc44] text-black font-bold px-4 py-2 border-2 border-black shadow-[3px_3px_0_0_#000] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[1px_1px_0_0_#000] active:shadow-none active:translate-x-[3px] active:translate-y-[3px] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          title="导出档案为 JSON"
        >
          [↓] 导出卷宗 〈 EXPORT 〉
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        {/* 左侧：智能全屏高度，增加间距 */}
        <section className="xl:col-span-5 flex flex-col xl:sticky xl:top-4 xl:h-[calc(100vh-8rem)] bg-[#fcfaf2]">
          <fieldset className="border-4 border-black p-4 md:p-6 relative flex flex-col flex-grow bg-[#fcfaf2]">
            <legend className="px-3 text-lg font-black tracking-widest bg-[#fcfaf2] text-black">
              思想刻录 〈 ENGRAVE 〉
            </legend>

            <div className="text-xs font-bold text-[#ff3333] mb-6 border-b-2 border-dashed border-black pb-3">
              ※ 注：可跳过任意题目，留白亦是回答。
            </div>

            {/* 增加了 space-y-10 提升呼吸感 */}
            <form className="space-y-10 overflow-y-auto pr-4 custom-retro-scroll flex-grow pb-8 bg-[#fcfaf2]">
              {questions.map((question, idx) => (
                <div key={idx} className="space-y-3">
                  <label
                    htmlFor={`dossier-q-${idx}`}
                    className="flex items-start text-base font-bold leading-relaxed cursor-pointer text-black"
                  >
                    <span className="bg-black text-white px-2 py-0.5 mr-3 shrink-0 shadow-[2px_2px_0_0_#ffcc00]">
                      Q {String(idx).padStart(2, "0")}
                    </span>
                    <span className="pt-0.5">{question}</span>
                  </label>
                  <textarea
                    id={`dossier-q-${idx}`}
                    className="w-full bg-white text-black border-2 border-black rounded-none p-4 text-base focus:outline-none focus:ring-0 focus:shadow-[6px_6px_0_0_#ffcc00] transition-shadow resize-y min-h-[120px] shadow-[2px_2px_0_0_#000]"
                    placeholder="输入你想说的话..."
                    value={formData[idx]}
                    onChange={(e) => handleInputChange(idx, e.target.value)}
                  />
                </div>
              ))}
            </form>

            <div className="mt-6 pt-6 border-t-4 border-black shrink-0 bg-[#fcfaf2]">
              {submitMessage.text && (
                <div
                  className={`mb-4 p-3 font-bold text-sm border-2 border-black text-black ${submitMessage.type === "error" ? "bg-[#ff6b6b]" : "bg-[#4ade80]"}`}
                >
                  {submitMessage.text}
                </div>
              )}

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={isSubmitting || !user}
                  className="flex-grow bg-[#ffcc00] text-black font-black text-lg py-3 px-4 border-4 border-black shadow-[4px_4px_0_0_#000] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0_0_#000] active:shadow-none active:translate-x-[4px] active:translate-y-[4px] transition-all disabled:opacity-50"
                >
                  {isSubmitting ? "正在封存..." : "👉 归档印封 〈 SEAL 〉"}
                </button>

                <button
                  type="button"
                  onClick={() => setFormData(Array(questions.length).fill(""))}
                  className="bg-[#ff6b6b] text-black font-black py-3 px-4 border-4 border-black shadow-[4px_4px_0_0_#000] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0_0_#000] active:shadow-none active:translate-x-[4px] active:translate-y-[4px] transition-all"
                  title="清空表单"
                >
                  X 清空
                </button>
              </div>
            </div>
          </fieldset>
        </section>

        {/* 右侧：同步改为智能全屏高度，增加间距 */}
        <section className="xl:col-span-7 flex flex-col xl:h-[calc(100vh-8rem)] overflow-y-auto custom-retro-scroll pr-2 bg-[#fcfaf2]">
          <fieldset className="border-4 border-black p-4 md:p-6 relative flex flex-col min-h-full bg-[#fcfaf2]">
            <legend className="px-3 text-lg font-black tracking-widest bg-[#fcfaf2] text-black">
              历史卷宗 〈 ARCHIVES 〉
            </legend>

            {loadingDb ? (
              <div className="py-20 text-center font-bold text-lg animate-pulse text-black">
                [系统] 正在同步异星节点数据...
              </div>
            ) : answersFeed.length === 0 ? (
              <div className="py-20 text-center font-bold border-2 border-dashed border-black text-black">
                【 查无记录，等待第一位先驱者 】
              </div>
            ) : (
              <div className="space-y-8 pt-4">
                {answersFeed.map((feed) => (
                  <article
                    key={feed.id}
                    className="bg-white border-4 border-black shadow-[6px_6px_0_0_#111] overflow-hidden"
                  >
                    <div className="bg-black text-white px-5 py-3 flex flex-wrap justify-between items-center border-b-4 border-black">
                      <div className="font-bold tracking-widest text-sm">
                        [ID:{" "}
                        <span className="text-[#ffcc00]">
                          {feed.userId?.substring(0, 6) || "UNKNOWN"}
                        </span>
                        ]
                      </div>
                      <div className="text-xs font-bold">
                        TIMESTAMP: {formatTime(feed.createdAt)}
                      </div>
                    </div>

                    <div className="p-6 space-y-8">
                      {feed.answers &&
                        feed.answers.map((item, i) => (
                          <div key={i} className="space-y-3">
                            <div className="flex items-start gap-3">
                              <span className="text-sm font-bold bg-black text-white px-2 py-0.5 shrink-0 shadow-[2px_2px_0_0_#88cc44]">
                                Q {String(item.qId !== undefined ? item.qId : i).padStart(2, "0")}
                              </span>
                              <h4 className="text-sm font-bold text-black leading-relaxed pt-0.5">
                                {item.question}
                              </h4>
                            </div>
                            <div className="pl-4 border-l-4 border-black text-base whitespace-pre-wrap leading-relaxed font-medium text-gray-800 ml-2">
                              {item.answer}
                            </div>
                          </div>
                        ))}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </fieldset>
        </section>
      </div>

      <style
        dangerouslySetInnerHTML={{
          __html: `
        /* 粗犷风滚动条 */
        .custom-retro-scroll::-webkit-scrollbar {
          width: 12px;
        }
        .custom-retro-scroll::-webkit-scrollbar-track {
          background: #fcfaf2;
          border-left: 2px solid #000;
        }
        .custom-retro-scroll::-webkit-scrollbar-thumb {
          background-color: #000;
          border: 2px solid #fcfaf2;
        }
      `,
        }}
      />
    </div>
  );
}