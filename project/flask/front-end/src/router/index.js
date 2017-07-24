import Vue from 'vue'
import Router from 'vue-router'
import Search from '@/components/Search'
import Request from '@/components/Request'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Search
    },
    {
      path: '/cloud',
      name: 'Cloud',
      component: Request
    }
  ]
})
