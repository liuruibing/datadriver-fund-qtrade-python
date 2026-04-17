// import { onBeforeUnmount } from 'vue';
 
export default function useAbortController() {
  const controllers = new Map(); // 用 Map 存储多个控制器
 
  // 添加控制器
   const createSignal = (requestId: string) => {
    const controller = new AbortController();
    controllers.set(requestId, controller);
    return controller.signal;
  };
 
  // 取消特定请求
  const abortRequest = (requestId: string) => {
    if (controllers.has(requestId)) {
      controllers.get(requestId).abort();
      controllers.delete(requestId);
    }
  };
 
  // 自动清理
  // onBeforeUnmount(() => {
  //   controllers.forEach(controller => controller.abort());
  //   controllers.clear();
  // });
 
  return { createSignal, abortRequest };
}