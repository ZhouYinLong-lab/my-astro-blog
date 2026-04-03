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

// --- Firebase 初始化 (容错装甲) ---
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

const ITEMS_PER_PAGE = 6; // 每页显示 6 张卡片，完美平衡左侧高度

export default function DossierArchive({
  title = "柳含知的问卷",
  subtitle = "留下自己的思考（填写后您的回答将被公开）",
  questions = [],
  archiveId = "default_archive",
}) {
  const [user, setUser] = useState(null);
  const [answersFeed, setAnswersFeed] = useState([]);
  const [loadingDb, setLoadingDb] = useState(true);

  // 表单状态
  const [formData, setFormData] = useState(Array(questions.length).fill(""));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState({ type: "", text: "" });

  // 分页与详情状态
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedDossier, setSelectedDossier] = useState(null); 

  // 1. 初始化 Auth
  useEffect(() => {
    if (!auth) return;
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== "undefined" && __initial_auth_token) {
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

  // 2. 监听数据库
  useEffect(() => {
    if (!user || !db || !archiveId) return;

    const colRef = collection(db, "artifacts", appId, "public", "data", archiveId);
    const q = query(colRef);

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const docs = snapshot.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        }));

        docs.sort((a, b) => {
          const timeA = a.createdAt?.toMillis ? a.createdAt.toMillis() : a.createdAt || 0;
          const timeB = b.createdAt?.toMillis ? b.createdAt.toMillis() : b.createdAt || 0;
          return timeB - timeA;
        });

        setAnswersFeed(docs);
        setLoadingDb(false);
      },
      (error) => {
        console.error("Firestore fetch error:", error);
        setLoadingDb(false);
      }
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
    if (isSubmitting) return; // 拦截连点器
    if (!user || !db) {
      setSubmitMessage({ type: "error", text: "[！通信中断]请稍后再试。" });
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
      setSubmitMessage({ type: "error", text: "[！空白卷宗]请至少作答一问。" });
      return;
    }

    setIsSubmitting(true);
    setSubmitMessage({ type: "", text: "" });

    try {
      const colRef = collection(db, "artifacts", appId, "public", "data", archiveId);
      await addDoc(colRef, {
        userId: user.uid,
        answers: filledAnswers,
        createdAt: serverTimestamp(),
      });

      setSubmitMessage({ type: "success", text: "[√ 封存完毕]已刻录至底层档案。" });
      setFormData(Array(questions.length).fill(""));
      setCurrentPage(1); // 提交后强制跳回第一页
      setTimeout(() => setSubmitMessage({ type: "", text: "" }), 3000);
    } catch (err) {
      setSubmitMessage({ type: "error", text: `[！封装异常]${err.message}` });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleExportData = () => {
    if (answersFeed.length === 0) return;
    const exportData = answersFeed.map((feed) => ({
      agentId: `Agent_${feed.userId?.substring(0, 6)}`,
      submittedAt: formatTime(feed.createdAt),
      answers: feed.answers.map((a) => ({ question: a.question, answer: a.answer })),
    }));
    const dataStr = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(exportData, null, 2))}`;
    const downloadAnchorNode = document.createElement("a");
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `${archiveId}_archive.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return "时空同步中...";
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
    return date.toLocaleString("zh-CN", {
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit",
    });
  };

  // --- 幽灵数据防御算法：强制钳制分页 ---
  const totalPages = Math.max(1, Math.ceil(answersFeed.length / ITEMS_PER_PAGE));
  const safePage = Math.min(currentPage, totalPages);
  const currentFeed = answersFeed.slice((safePage - 1) * ITEMS_PER_PAGE, safePage * ITEMS_PER_PAGE);

  // ============================================================================
  // 渲染模式 2：全屏详情页 (模拟跳转新网页的折跃模式)
  // ============================================================================
  if (selectedDossier) {
    return (
      // 沉浸式护盾 bg-[#fcfaf2] 彻底遮盖底层所有元素
      <div className="fixed inset-0 z-50 bg-[#fcfaf2] overflow-y-auto font-mono text-black">
        <div className="max-w-4xl mx-auto p-4 md:p-8 min-h-screen flex flex-col">
          {/* 详情页头部 */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 pb-6 border-b-8 border-black gap-4">
            <button
              type="button"
              onClick={() => setSelectedDossier(null)}
              className="bg-black text-white font-black px-6 py-3 border-4 border-black hover:bg-white hover:text-black transition-all flex items-center gap-2 shadow-[6px_6px_0_0_#ffcc00] active:translate-x-[2px] active:translate-y-[2px] active:shadow-[2px_2px_0_0_#ffcc00]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
              返回档案库
            </button>
            <div className="text-left sm:text-right">
              <h2 className="text-xl sm:text-2xl font-black tracking-widest uppercase">
                卷宗代号: {selectedDossier.userId?.substring(0, 6) || "UNKNOWN"}
              </h2>
              <p className="font-bold text-gray-600 mt-1">
                刻录时间: {formatTime(selectedDossier.createdAt)}
              </p>
            </div>
          </div>

          {/* 详情页问答内容 - 纯净阅读区 */}
          <div className="bg-white border-4 border-black shadow-[12px_12px_0_0_#111] p-6 md:p-12 flex-grow space-y-12">
            {selectedDossier.answers.map((item, i) => (
              <div key={i} className="space-y-4">
                <div className="flex items-start gap-4">
                  <span className="text-lg font-black bg-black text-white px-3 py-1 shrink-0 shadow-[4px_4px_0_0_#88cc44]">
                    Q {String(item.qId !== undefined ? item.qId : i).padStart(2, "0")}
                  </span>
                  <h4 className="text-lg sm:text-xl font-bold leading-relaxed pt-1">
                    {item.question}
                  </h4>
                </div>
                <div className="pl-6 border-l-8 border-black text-base sm:text-lg whitespace-pre-wrap leading-loose font-medium text-gray-800 ml-4 py-2 bg-gray-50 pr-4">
                  {item.answer}
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-12 text-center font-bold text-gray-400 tracking-widest pb-8">
            — 档案阅览结束 —
          </div>
        </div>
      </div>
    );
  }

  // ============================================================================
  // 渲染模式 1：主页 (左右分栏，弹性拉伸，右侧底部分页)
  // ============================================================================
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
          className="mt-4 md:mt-0 flex items-center gap-2 bg-[#88cc44] text-black font-bold px-4 py-2 border-2 border-black shadow-[3px_3px_0_0_#000] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[1px_1px_0_0_#000] active:shadow-none transition-all disabled:opacity-50"
        >
          [↓] 导出卷宗 〈 EXPORT 〉
        </button>
      </div>

      {/* 核心布局：左右弹性等高拉伸 items-stretch */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-stretch">
        
        {/* ============ 左侧：问卷表单 ============ */}
        <section className="xl:col-span-6 flex flex-col bg-[#fcfaf2] h-full">
          <fieldset className="border-4 border-black p-4 md:p-6 relative flex flex-col h-full bg-[#fcfaf2]">
            <legend className="px-3 text-lg font-black tracking-widest bg-[#fcfaf2] text-black">
              思想刻录 〈 ENGRAVE 〉
            </legend>
            <div className="text-xs font-bold text-[#ff3333] mb-6 border-b-2 border-dashed border-black pb-3">
              ※ 注：可跳过任意题目，留白亦是回答。
            </div>

            <form className="space-y-10 flex-grow pb-8">
              {questions.map((question, idx) => (
                <div key={idx} className="space-y-3">
                  <label htmlFor={`dossier-q-${idx}`} className="flex items-start text-base font-bold leading-relaxed cursor-pointer text-black">
                    <span className="bg-black text-white px-2 py-0.5 mr-3 shrink-0 shadow-[2px_2px_0_0_#ffcc00]">
                      Q {String(idx).padStart(2, "0")}
                    </span>
                    <span className="pt-0.5">{question}</span>
                  </label>
                  <textarea
                    id={`dossier-q-${idx}`}
                    className="w-full bg-white text-black border-2 border-black rounded-none p-4 text-base focus:outline-none focus:shadow-[6px_6px_0_0_#ffcc00] transition-shadow resize-y min-h-[120px] shadow-[2px_2px_0_0_#000]"
                    placeholder="输入你想说的话..."
                    value={formData[idx]}
                    onChange={(e) => handleInputChange(idx, e.target.value)}
                  />
                </div>
              ))}
            </form>

            <div className="mt-6 pt-6 border-t-4 border-black shrink-0">
              {submitMessage.text && (
                <div className={`mb-4 p-3 font-bold text-sm border-2 border-black ${submitMessage.type === "error" ? "bg-[#ff6b6b]" : "bg-[#4ade80]"}`}>
                  {submitMessage.text}
                </div>
              )}
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={isSubmitting || !user}
                  className="flex-grow bg-[#ffcc00] text-black font-black text-lg py-3 px-4 border-4 border-black shadow-[4px_4px_0_0_#000] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0_0_#000] active:shadow-none transition-all disabled:opacity-50"
                >
                  {isSubmitting ? "正在封存..." : "👉 归档印封 〈 SEAL 〉"}
                </button>
                <button
                  type="button"
                  onClick={() => setFormData(Array(questions.length).fill(""))}
                  className="bg-[#ff6b6b] text-black font-black py-3 px-4 border-4 border-black shadow-[4px_4px_0_0_#000] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0_0_#000] active:shadow-none transition-all"
                >
                  X 清空
                </button>
              </div>
            </div>
          </fieldset>
        </section>

        {/* ============ 右侧：分页长方形卡片 ============ */}
        <section className="xl:col-span-6 flex flex-col bg-[#fcfaf2] h-full">
          <fieldset className="border-4 border-black p-4 md:p-6 relative flex flex-col h-full bg-[#fcfaf2]">
            <legend className="px-3 text-lg font-black tracking-widest bg-[#fcfaf2] text-black">
              历史卷宗 〈 ARCHIVES 〉
            </legend>

            {loadingDb ? (
              <div className="py-20 text-center font-bold text-lg animate-pulse text-black">
                [系统] 正在同步异星节点数据...
              </div>
            ) : answersFeed.length === 0 ? (
              <div className="py-20 text-center font-bold border-2 border-dashed border-black text-black flex-grow flex items-center justify-center">
                [ 查无记录，等待第一位先驱者 ]
              </div>
            ) : (
              <>
                {/* 固定的卡片列表，高度被 flex-grow 撑开以压住底部的分页栏 */}
                <div className="flex-grow space-y-5 pt-2">
                  {currentFeed.map((feed) => (
                    <button
                      type="button"
                      key={feed.id}
                      onClick={() => setSelectedDossier(feed)}
                      className="w-full text-left bg-white border-4 border-black p-5 shadow-[4px_4px_0_0_#111] hover:-translate-y-1 hover:shadow-[6px_6px_0_0_#ffcc00] active:translate-y-1 active:shadow-[2px_2px_0_0_#ffcc00] transition-all flex flex-col justify-between min-h-[8rem] relative group overflow-hidden"
                    >
                      <div className="flex flex-wrap justify-between items-start gap-2">
                        <div className="font-black text-lg md:text-xl tracking-wider text-black">
                          ID: {feed.userId?.substring(0, 6) || "UNKNOWN"}
                        </div>
                        <div className="bg-black text-white text-xs font-bold px-2 py-1 shrink-0">
                          已密封
                        </div>
                      </div>
                      <div className="text-xs md:text-sm font-bold text-gray-500 mt-4 md:mt-auto">
                        TIME: {formatTime(feed.createdAt)}
                      </div>
                      {/* Hover时滑入的“点击查看”提示 */}
                      <div className="absolute inset-0 bg-black/90 flex items-center justify-center translate-y-full group-hover:translate-y-0 transition-transform duration-300">
                        <span className="text-[#ffcc00] font-black tracking-widest text-lg flex items-center gap-2">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                          展开卷宗
                        </span>
                      </div>
                    </button>
                  ))}
                </div>

                {/* 翻页控制器 (强制沉底) */}
                <div className="mt-6 pt-5 border-t-4 border-black flex flex-wrap justify-between items-center shrink-0 gap-4">
                  <button
                    type="button"
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={safePage === 1}
                    className="font-bold text-black border-2 border-black bg-white px-4 py-2 hover:bg-black hover:text-white transition-colors disabled:opacity-30 disabled:hover:bg-white disabled:hover:text-black"
                  >
                    ← 上页
                  </button>
                  <span className="font-black text-lg tracking-widest">
                    {String(safePage).padStart(2, "0")} / {String(totalPages).padStart(2, "0")}
                  </span>
                  <button
                    type="button"
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={safePage === totalPages}
                    className="font-bold text-black border-2 border-black bg-white px-4 py-2 hover:bg-black hover:text-white transition-colors disabled:opacity-30 disabled:hover:bg-white disabled:hover:text-black"
                  >
                    下页 →
                  </button>
                </div>
              </>
            )}
          </fieldset>
        </section>

      </div>
    </div>
  );
}