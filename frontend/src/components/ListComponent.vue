<script>import PostComponent from './PostComponent.vue'
import {ref, onMounted, onUnmounted} from 'vue'
import getPosts from '../scripts/post-loader'

const posts = ref(getPosts(10))</script>