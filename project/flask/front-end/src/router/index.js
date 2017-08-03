import Vue from 'vue'
import Router from 'vue-router'
import Search from '@/components/Search'
import Request from '@/components/Request'
import Test from '@/components/Test'

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
      path: '/ajaxfiletest',
      name: 'ajaxtest',
      component: Test
    },
    {
      path: '/cloud/:query',
      name: 'Cloud',
      component: Request,
      props: true
    }
  ]
})
