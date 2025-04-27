/// <reference types="vite/client" />

interface ImportMeta {
  readonly env: {
    readonly VITE_CLERK_PUBLISHABLE_KEY: string;
    [key: string]: string;
  };
}
