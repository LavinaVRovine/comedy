import { createRouter, createWebHistory } from 'vue-router'
import store from "@/store";
import Home from '../views/Home.vue'
import SignUp from "@/views/SignUp";
import LogIn from "@/views/LogIn";
import MyAccount from "@/views/MyAccount";


const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
    {
    path: '/sign-up',
    name: 'SignUp',
    component: SignUp
  },{
    path: '/my-account',
    name: 'MyAccount',
    component: MyAccount,
    meta:{
      requireLogin: true,
    }
  },
    {
    path: '/log-in',
    name: 'LogIn',
    component: LogIn
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach(
    (to, from, next) =>{
      if (to.matched.some(record => record.meta.requireLogin) && !store.state.isAuthenticated){
        next(
            {name:"LogIn", query: {to: to.path}}
        )
      }
      else {
        next()
      }
    }
)

export default router
