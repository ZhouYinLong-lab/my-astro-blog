import { useState } from "react";

const DEFAULT_API_URL = "https://api.zylatent.com";

export default function FastApiPlayground({ apiBaseUrl = DEFAULT_API_URL }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const callApi = async (path) => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${apiBaseUrl}${path}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}`);
      }

      setResult(data);
    } catch (requestError) {
      setResult(null);
      setError(
        `调用失败：${requestError.message}。如果你正在本地阅读，请先确认线上 API 已部署。`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="my-8 border-2 border-black bg-[#fcfaf2] p-4 shadow-[6px_6px_0_0_#111] dark:border-white dark:bg-zinc-900 dark:shadow-[6px_6px_0_0_#000]">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b-2 border-black pb-3 dark:border-white">
        <div>
          <h3 className="m-0 text-lg font-black text-black dark:text-white">
            动手试试：调用寒柳别苑 API
          </h3>
          <p className="m-0 mt-1 text-sm text-zinc-700 dark:text-zinc-300">
            当前地址：<code>{apiBaseUrl}</code>
          </p>
        </div>
        <span className="border-2 border-black bg-[#ffcc00] px-2 py-1 text-xs font-black text-black dark:border-white">
          GET
        </span>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => callApi("/api/site")}
          disabled={loading}
          className="border-2 border-black bg-white px-3 py-2 font-bold text-black shadow-[3px_3px_0_0_#111] transition hover:-translate-y-0.5 disabled:cursor-wait disabled:opacity-60 dark:border-white dark:bg-zinc-800 dark:text-white dark:shadow-[3px_3px_0_0_#000]"
        >
          获取站点资料
        </button>
        <button
          type="button"
          onClick={() => callApi("/api/posts?category=尺蠖&limit=10")}
          disabled={loading}
          className="border-2 border-black bg-white px-3 py-2 font-bold text-black shadow-[3px_3px_0_0_#111] transition hover:-translate-y-0.5 disabled:cursor-wait disabled:opacity-60 dark:border-white dark:bg-zinc-800 dark:text-white dark:shadow-[3px_3px_0_0_#000]"
        >
          查询文章列表
        </button>
        <button
          type="button"
          onClick={() => callApi("/health")}
          disabled={loading}
          className="border-2 border-black bg-white px-3 py-2 font-bold text-black shadow-[3px_3px_0_0_#111] transition hover:-translate-y-0.5 disabled:cursor-wait disabled:opacity-60 dark:border-white dark:bg-zinc-800 dark:text-white dark:shadow-[3px_3px_0_0_#000]"
        >
          检查服务状态
        </button>
      </div>

      {loading && <p className="mt-4 font-bold text-black dark:text-white">请求中……</p>}
      {error && (
        <p className="mt-4 border-2 border-red-700 bg-red-100 p-3 font-bold text-red-900 dark:bg-red-950 dark:text-red-100">
          {error}
        </p>
      )}
      {result && (
        <pre className="mt-4 max-h-80 overflow-auto border-2 border-black bg-zinc-950 p-4 text-sm leading-relaxed text-green-300 dark:border-white">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
