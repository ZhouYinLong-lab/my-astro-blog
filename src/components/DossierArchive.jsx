import { initializeApp } from "firebase/app";
import { getAuth, onAuthStateChanged, signInAnonymously } from "firebase/auth";
import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  getFirestore,
  onSnapshot,
  query,
  serverTimestamp,
} from "firebase/firestore";
import { useEffect, useState } from "react";

// --- Firebase 初始化 ---
let app;
let auth;
let db;
let appId;

try {
  const firebaseConfig = {
    apiKey: "AIzaSyAJlPY7rPbm3C9uwq86ZDudyNXipAbMOW0",
    authDomain: "humanities-archive.firebaseapp.com",
    projectId: "humanities-archive",
    storageBucket: "humanities-archive.firebasestorage.app",
    messagingSenderId: "792290793856",
    appId: "1:792290793856:web:81386fdd50f15712fa8965",
    measurementId: "G-Z011CNZMXP",
  };
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
  db = getFirestore(app);
  appId = firebaseConfig.appId;
} catch (error) {
  console.error("Firebase config error:", error);
}

const ITEMS_PER_PAGE = 12;

export default function DossierArchive({
  title = "柳含知的问卷",
  subtitle = "留下自己的思考（填写后您的回答将被公开）",
  questions = [],
  archiveId = "default_archive",
}) {
  const [user, setUser] = useState(null);
  const [answersFeed, setAnswersFeed] = useState([]);
  const [loadingDb, setLoadingDb] = useState(true);

  const [formData, setFormData] = useState(Array(questions.length).fill(""));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState({ type: "", text: "" });

  const [currentPage, setCurrentPage] = useState(1);
  const [selectedDossier, setSelectedDossier] = useState(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  const [isAdmin, setIsAdmin] = useState(false);
  const [adminClickCount, setAdminClickCount] = useState(0);
  const [showAdminModal, setShowAdminModal] = useState(false);
  const [adminPwd, setAdminPwd] = useState("");

  // 💡 核心修复：放宽匹配条件，只要题目包含“你是”即可精准定位
  const whoAreYouIndex = questions.findIndex((q) => q.includes("你是"));

  useEffect(() => {
    if (localStorage.getItem("dossier_god_mode") === "true") {
      setIsAdmin(true);
    }

    if (!auth) return;
    const initAuth = async () => {
      try {
        await signInAnonymously(auth);
      } catch (err) {
        console.error("Auth init failed:", err);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

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
    if (isSubmitting) return;
    if (!user || !db) {
      setSubmitMessage({ type: "error", text: "! 通信中断：请稍后再试。" });
      return;
    }

    // 校验必填项
    if (whoAreYouIndex !== -1 && formData[whoAreYouIndex].trim() === "") {
      setSubmitMessage({ type: "error", text: "! 协议拦截：请务必回答身份标识题目。" });
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
      setSubmitMessage({ type: "error", text: "! 空白卷宗：请至少作答一问。" });
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
      setSubmitMessage({ type: "success", text: "√ 封存完毕：已刻录至底层档案。" });
      setFormData(Array(questions.length).fill(""));
      setCurrentPage(1);
      setTimeout(() => setSubmitMessage({ type: "", text: "" }), 3000);
    } catch (err) {
      setSubmitMessage({ type: "error", text: `! 封装异常：${err.message}` });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteDossier = async (e, docId) => {
    e.stopPropagation();
    try {
      await deleteDoc(doc(db, "artifacts", appId, "public", "data", archiveId, docId));
      setDeleteConfirmId(null);
      if (selectedDossier?.id === docId) {
        setSelectedDossier(null);
      }
    } catch (err) {
      console.error("Delete failed:", err);
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
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleTitleClick = () => {
    if (isAdmin) return;
    const newCount = adminClickCount + 1;
    if (newCount >= 5) {
      setShowAdminModal(true);
      setAdminClickCount(0);
    } else {
      setAdminClickCount(newCount);
    }
  };

  const totalPages = Math.max(1, Math.ceil(answersFeed.length / ITEMS_PER_PAGE));
  const safePage = Math.min(currentPage, totalPages);
  const currentFeed = answersFeed.slice((safePage - 1) * ITEMS_PER_PAGE, safePage * ITEMS_PER_PAGE);

  if (selectedDossier) {
    // 💡 核心修复：全屏详情页提取条件放宽为“你是”
    const detailWhoItem = selectedDossier.answers.find((a) => a.question.includes("你是"));
    const detailWhoText = detailWhoItem ? detailWhoItem.answer : "未知节点的旅人";

    return (
      <div className="fixed inset-0 z-50 bg-[#fcfaf2] overflow-y-auto font-mono text-black">
        <div className="max-w-4xl mx-auto p-4 md:p-8 min-h-screen flex flex-col">
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
            <div className="text-left sm:text-right flex flex-col items-start sm:items-end">
              <h2 className="text-xl sm:text-2xl font-black tracking-widest uppercase">
                ID: {selectedDossier.userId?.substring(0, 6) || "UNKNOWN"}
              </h2>
              <p className="font-black text-gray-800 mt-2 text-lg">
                来自 {detailWhoText}
              </p>
              <p className="font-bold text-gray-500 mt-1">
                刻录时间: {formatTime(selectedDossier.createdAt)}
              </p>
              {(user?.uid === selectedDossier.userId || isAdmin) && (
                <div className="mt-4">
                  {deleteConfirmId === selectedDossier.id ? (
                    <div className="flex gap-2">
                      <button type="button" onClick={(e) => handleDeleteDossier(e, selectedDossier.id)} className="bg-red-600 text-white font-bold px-3 py-1.5 border-2 border-black hover:bg-red-500 shadow-[2px_2px_0_0_#000] active:shadow-none active:translate-x-[2px] active:translate-y-[2px] transition-all">确认销毁？</button>
                      <button type="button" onClick={() => setDeleteConfirmId(null)} className="bg-gray-300 text-black font-bold px-3 py-1.5 border-2 border-black hover:bg-gray-200 shadow-[2px_2px_0_0_#000] active:shadow-none active:translate-x-[2px] active:translate-y-[2px] transition-all">取消</button>
                    </div>
                  ) : (
                    <button type="button" onClick={() => setDeleteConfirmId(selectedDossier.id)} className="bg-[#ff3333] text-white font-bold px-3 py-1.5 border-2 border-black shadow-[2px_2px_0_0_#000] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[1px_1px_0_0_#000] active:shadow-none active:translate-x-[2px] active:translate-y-[2px] transition-all">
                      [X] 销毁此卷宗 {isAdmin && user?.uid !== selectedDossier.userId && "(管理员强制)"}
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>

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

  return (
    <div className="bg-[#fcfaf2] text-black font-mono p-4 md:p-8 border-4 border-black shadow-[8px_8px_0_0_#111] relative">
      {showAdminModal && (
        <div className="fixed inset-0 z-[9999] bg-black/80 flex items-center justify-center p-4">
          <div className="bg-[#fcfaf2] border-4 border-black p-6 shadow-[8px_8px_0_0_#ffcc00] max-w-sm w-full">
            <h3 className="text-xl font-black mb-4 uppercase text-black">System Override</h3>
            <p className="text-sm font-bold mb-4">请输入站长访问密钥：</p>
            <input
              type="password"
              value={adminPwd}
              onChange={(e) => setAdminPwd(e.target.value)}
              className="w-full border-2 border-black p-2 mb-4 text-black focus:outline-none focus:shadow-[4px_4px_0_0_#000]"
              placeholder="Access Code..."
            />
            <div className="flex justify-end gap-4 items-center">
              <button type="button" onClick={() => {setShowAdminModal(false); setAdminPwd("");}} className="font-bold text-gray-500 hover:text-black">取消</button>
              <button
                type="button"
                onClick={() => {
                  if (adminPwd === "frosti") {
                    setIsAdmin(true);
                    localStorage.setItem("dossier_god_mode", "true");
                    setShowAdminModal(false);
                    setAdminPwd("");
                  } else {
                    setAdminPwd("");
                  }
                }}
                className="bg-black text-white font-bold px-4 py-2 border-2 border-black hover:translate-x-[2px] hover:translate-y-[2px] shadow-[4px_4px_0_0_#ffcc00] active:shadow-none transition-all"
              >
                解锁权限
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 border-b-4 border-black pb-4">
        <div>
          <h2 
            onClick={handleTitleClick}
            className="text-2xl md:text-4xl font-black tracking-widest mb-2 uppercase text-black select-none cursor-pointer"
            title={isAdmin ? "God Mode Activated" : ""}
          >
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

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-stretch">
        <section className="xl:col-span-6 flex flex-col bg-[#fcfaf2] h-full">
          <fieldset className="border-4 border-black p-4 md:p-6 relative flex flex-col h-full bg-[#fcfaf2]">
            <legend className="px-3 text-lg font-black tracking-widest bg-[#fcfaf2] text-black">
              思想刻录 〈 ENGRAVE 〉
            </legend>
            <div className="text-xs font-bold text-[#ff3333] mb-6 border-b-2 border-dashed border-black pb-3">
              ※ 注：带 * 号为必填身份标识，其余题目可自由跳过，留白亦是回答。
            </div>

            <form className="space-y-10 flex-grow pb-8">
              {questions.map((question, idx) => (
                <div key={idx} className="space-y-3">
                  <label htmlFor={`dossier-q-${idx}`} className="flex items-start text-base font-bold leading-relaxed cursor-pointer text-black">
                    <span className="bg-black text-white px-2 py-0.5 mr-3 shrink-0 shadow-[2px_2px_0_0_#ffcc00]">
                      Q {String(idx).padStart(2, "0")}
                    </span>
                    <span className="pt-0.5">
                      {question}
                      {idx === whoAreYouIndex && <span className="text-[#ff3333] ml-2 font-black">*</span>}
                    </span>
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
                <div className={`mb-4 p-3 font-bold text-sm border-2 border-black text-black ${submitMessage.type === "error" ? "bg-[#ff6b6b]" : "bg-[#4ade80]"}`}>
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

        <section className="xl:col-span-6 flex flex-col bg-[#fcfaf2] h-full">
          <fieldset className="border-4 border-black p-4 md:p-6 relative flex flex-col h-full bg-[#fcfaf2]">
            <legend className="px-3 text-lg font-black tracking-widest bg-[#fcfaf2] text-black">
              历史卷宗 〈 ARCHIVES 〉
            </legend>

            {loadingDb ? (
              <div className="py-20 text-center font-bold text-lg animate-pulse text-black">
                系统正在同步异星节点数据...
              </div>
            ) : answersFeed.length === 0 ? (
              <div className="py-20 text-center font-bold border-2 border-dashed border-black text-black flex-grow flex items-center justify-center">
                查无记录，等待第一位先驱者
              </div>
            ) : (
              <>
                <div className="flex-grow space-y-5 pt-2">
                  {currentFeed.map((feed) => {
                    // 💡 核心修复：卡片提取条件放宽为“你是”
                    const whoAnswerItem = feed.answers?.find((a) => a.question.includes("你是"));
                    const whoAnswerText = whoAnswerItem ? whoAnswerItem.answer : "未知节点的旅人";

                    return (
                      <div
                        key={feed.id}
                        role="button"
                        tabIndex={0}
                        onClick={() => setSelectedDossier(feed)}
                        className={`w-full text-left border-4 border-black p-5 shadow-[4px_4px_0_0_#111] hover:-translate-y-1 hover:shadow-[6px_6px_0_0_#ffcc00] active:translate-y-1 active:shadow-[2px_2px_0_0_#ffcc00] transition-all flex flex-col justify-between min-h-[8rem] relative group overflow-hidden cursor-pointer ${isAdmin ? "bg-gray-100" : "bg-white"}`}
                      >
                        <div className="flex flex-wrap justify-between items-start gap-2 relative z-20">
                          <div className="font-black text-lg md:text-xl tracking-wider text-black group-hover:text-white transition-colors duration-300">
                            ID: {feed.userId?.substring(0, 6) || "UNKNOWN"}
                            <div className="text-sm font-bold mt-1 text-gray-600 group-hover:text-gray-300 transition-colors duration-300">
                              来自 {whoAnswerText}
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            {(user?.uid === feed.userId || isAdmin) && (
                              deleteConfirmId === feed.id ? (
                                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                                  <button type="button" onClick={(e) => handleDeleteDossier(e, feed.id)} className="bg-red-600 text-white text-xs font-bold px-2 py-1 border-2 border-black hover:bg-red-500 shadow-[2px_2px_0_0_#000] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0_0_#000] active:shadow-none transition-all">确认销毁</button>
                                  <button type="button" onClick={() => setDeleteConfirmId(null)} className="bg-gray-300 text-black text-xs font-bold px-2 py-1 border-2 border-black hover:bg-gray-200 shadow-[2px_2px_0_0_#000] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0_0_#000] active:shadow-none transition-all">取消</button>
                                </div>
                              ) : (
                                <button type="button" onClick={(e) => { e.stopPropagation(); setDeleteConfirmId(feed.id); }} className="bg-[#ff3333] text-white text-xs font-bold px-2 py-1 border-2 border-black shadow-[2px_2px_0_0_#000] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0_0_#000] active:shadow-none transition-all">
                                  [X] 销毁
                                </button>
                              )
                            )}
                            <div className="bg-black text-white text-xs font-bold px-2 py-1 shrink-0 group-hover:bg-white group-hover:text-black transition-colors duration-300">
                              已密封
                            </div>
                          </div>
                        </div>
                        
                        <div className="text-xs md:text-sm font-bold text-gray-500 mt-4 md:mt-auto relative z-20 group-hover:text-gray-300 transition-colors duration-300">
                          TIME: {formatTime(feed.createdAt)}
                        </div>
                        
                        <div className="absolute inset-0 bg-black/90 flex items-center justify-center translate-y-full group-hover:translate-y-0 transition-transform duration-300 z-10 pointer-events-none">
                          <span className="text-[#ffcc00] font-black tracking-widest text-lg flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                            展开卷宗
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>

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