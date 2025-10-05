export interface DeferredPromise<T = void> {
  promise: Promise<T>
  resolve: (value: T | PromiseLike<T>) => void
  reject: (reason?: Error) => void
}

export function defer<T = void>(): DeferredPromise<T> {
  let resolve: (value: T | PromiseLike<T>) => void
  let reject: (reason?: Error) => void
  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve: resolve!, reject: reject! }
}
