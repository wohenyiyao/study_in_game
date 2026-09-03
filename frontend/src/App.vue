<template>
  <div class="app-shell">
    <!-- 装饰性渐变光斑背景 -->
    <div class="bg-deco" aria-hidden="true">
      <span class="blob b1"></span>
      <span class="blob b2"></span>
      <span class="blob b3"></span>
    </div>
    <router-view />
  </div>
</template>

<style scoped>
.app-shell {
  position: relative;
  min-height: 100%;
}
.bg-deco {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.5;
  animation: drift 18s ease-in-out infinite alternate;
}
.b1 {
  width: 480px;
  height: 480px;
  top: -160px;
  right: -120px;
  background: radial-gradient(circle at 35% 35%, rgba(139, 92, 246, 0.55), rgba(139, 92, 246, 0) 70%);
}
.b2 {
  width: 520px;
  height: 520px;
  bottom: -180px;
  left: -160px;
  background: radial-gradient(circle at 60% 40%, rgba(34, 211, 238, 0.4), rgba(34, 211, 238, 0) 70%);
  animation-delay: -6s;
}
.b3 {
  width: 300px;
  height: 300px;
  top: 38%;
  left: 55%;
  background: radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.4), rgba(99, 102, 241, 0) 70%);
  animation-delay: -11s;
}
@keyframes drift {
  0% {
    transform: translate(0, 0) scale(1);
  }
  100% {
    transform: translate(-40px, 30px) scale(1.12);
  }
}
</style>
