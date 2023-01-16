<template>
  <div class="box">
    <figure class="image mb-4">
      <!--            <img :src="content.thumbnails.high.url">-->
    </figure>

    <h3 class="is-size-4">{{ post.title }}</h3>
    <p>{{ post.description }}</p>
  </div>
</template>
<script>  export default {props: {post: Object}}</script>