import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import store from './store'
import axios from "axios";
// import VueObserveVisibility from "vue-observe-visibility";
import { ObserveVisibility } from 'vue-observe-visibility'

axios.defaults.baseURL = 'http://localhost:8000/'
let app = createApp(App)
app.use(store)
app.use(router, axios)
// app.use(VueObserveVisibility)
// https://github.com/Akryum/vue-observe-visibility/issues/219#issuecomment-683460059
app.directive('observe-visibility', {
  beforeMount: (el, binding, vnode) => {
    vnode.context = binding.instance;
    ObserveVisibility.bind(el, binding, vnode);
  },
  update: ObserveVisibility.update,
  unmounted: ObserveVisibility.unbind,
});

app.mount('#app')
// App.use(VueObserveVisibility);
