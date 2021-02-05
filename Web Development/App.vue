<template>
  <div class = 'main-container'>
    <amplify-chatbot
          bot-name="Test"
          bot-title="My ChatBot"
          welcome-message="Hello, how can I help you?"
          id = 'chatBot'
        />
    <amplify-authenticator>
      <!-- The rest of your app code -->


      <div id="app">
        <div class = 'container'>
          <div class = 'todo-container'>
            <h2>To Do App</h2>
            <input type = "text" v-model = "name" placeholder="Name your ToDo">
            <br>
            <input type = 'text' v-model="description" placeholder="Describe your task">
            <br>
            <button v-on:click = "createTodo" class = 'create-todo-button'>Create To Do</button>
            <div v-for="item in todos" :key="item.id" class = 'todo'>
              <h3>{{ item.name }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </div>
          <div class = 'user-info'>
            <h2>User Input:</h2>
            <p>Upload a Profile image-<input type="file" @change="uploadImage($event)"></p>


          </div>
          <div class = 'user-info'>
            <h2>User Info:</h2>
            <p>Skin Score: {{ userData.skinScoreQuan }}</p>
            <p>Skin Rating: {{ userData.skinScoreQual }}/100</p>
            <p>Skin Type: {{ userData.skinType }}</p>
            <p>Profile Image:</p>
            <img :src = "userData.profileImgUrl" class = 'profile-image'>
          </div>
        </div>
      </div>
      <amplify-sign-out></amplify-sign-out>
    </amplify-authenticator>
  </div>
</template>

<script>
import { API } from 'aws-amplify';
import { createTodo, createUser} from './graphql/mutations';
import { listTodos, getUser } from "@/graphql/queries";
import { onCreateTodo} from "@/graphql/subscriptions";
import { Auth } from 'aws-amplify';
import aws from 'aws-sdk';
//import { Interactions } from 'aws-amplify'
import { Hub, Logger } from 'aws-amplify';
const logger = new Logger('My-Logger');

// You can get the current config object
//const currentConfig = Auth.configure();

export default {
  name: 'App',
  async created() {
    this.getId();
    this.getTodos();
    this.subscribe();
    this.cogListener();

  },
  data(){
    return{
      name: '',
      description: '',
      todos: [],
      id: '',
      userData: {},

    }
  },
   mounted() {
    const chatbotElement = this.$el.querySelector("amplify-chatbot");
      chatbotElement.addEventListener("chatCompleted", this.handleComplete);
  },
  beforeUnmount() {
    const chatbotElement = this.$el.querySelector("amplify-chatbot");
    chatbotElement.removeEventListener("chatCompleted", this.handleComplete);
  },
  methods: {
    cogListener(){
      const listener = (data) => {
    switch (data.payload.event) {
      case 'signIn':
        logger.info('user signed in');
        console.log('signy inny bucko');
        this.getId();


        break;
      case 'signUp':
        logger.info('user signed up');

        break;
      case 'signOut':
        logger.info('user signed out');
        break;
      case 'signIn_failure':
        logger.error('user sign in failed');
        break;
      case 'tokenRefresh':
        logger.info('token refresh succeeded');
        break;
      case 'tokenRefresh_failure':
        logger.error('token refresh failed');
        break;
      case 'configured':
        logger.info('the Auth module is configured');
    }
  }
  Hub.listen('auth', listener);
    },

    handleComplete(event) {

      const { err, data } = event.detail;
      if (err) {
        console.log("bot conversation failed");
        console.log(err);

      }
      const user_info = data.slots;
      this.userData = {...this.userData, ...user_info}
      console.log(this.userData)


    },
    async createTodo() {
      const {name, description} = this;
      if (!name || !description) return;
      const todo = {name, description};
      console.log(name);
      await API.graphql({
        query: createTodo,
        variables: {input: todo},
      });
      this.name = '';
      this.description = '';
    },
    async getTodos (){
      const todos = await API.graphql({
        query: listTodos
      });
      this.todos = todos.data.listTodos.items;

    },
    subscribe () {
      API.graphql({ query: onCreateTodo})
      .subscribe({
        next: (eventData) => {
          let todo = eventData.value.data.onCreateTodo;
          if (this.todos.some(item => item.name === todo.name)) return; // remove duplications
          this.todos = [...this.todos, todo];
        }
        })
    },

    async getId() {
      let user = await Auth.currentAuthenticatedUser();
      const { attributes } = user;
      const user_id = attributes.sub
      this.id = user_id;
      console.log(this.id)
      var chatBot = document.getElementById('chatBot')
      chatBot.style.display = 'none'
      this.createNewUser();
      //this.getUserData();
    },

    async createNewUser (){

      console.log('creating new user in dynamo')

      const user_id = this.id
      const id = {'id': user_id}
      const userDetails = this.userData
      console.log(id)
      console.log(userDetails)

      await API.graphql({
        query: createUser,
        variables: {input: userDetails}
      })
    },

    async getUserData(){
      const id = this.id;

      const data = {id};
      const user = await API.graphql({
        query: getUser,
        variables: data,
      });

      try {
        const skinScoreQuan = user.data.getUser.skinScoreQuan;
        const skinType = user.data.getUser.skinType;

        const skinScoreQual = user.data.getUser.skinScoreQual;
        const profileImgUrl = user.data.getUser.profilePhotoLink;
        this.userData = {
        'skinScoreQuan': skinScoreQuan,
        'skinType': skinType,

          'skinScoreQual': skinScoreQual,
          'profileImgUrl': profileImgUrl
        }
      }
      catch (err) {
        console.log('error in getting user data')
      }
    },
    async uploadImage(event){
      const s3 = new aws.S3();
      aws.config.update({
        accessKeyId: '',//Removed for security
        secretAccessKey: ''//Removed for security
      });
      aws.config.region = 'eu-west-2'
      var file = event.target.files[0]
      const name = 'profilePic-'+this.id+'.png'


      s3.upload({
        Bucket: 'amplify-vue-practice',
        Key: name,
        Body: file
      }).promise();
      console.log('upload complete')
    }
  }
}


</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

amplify-chatbot{
  margin-top: 10%;
  padding-right: 5%;
}
.main-container {
  display: flex;
  flex-direction: row;
  align-content: center;
  justify-content: center;
}



.container {
  display: flex;
  flex-direction: row;
}
.todo-container {
  border: aqua 2px solid;
  border-radius: 10px;
  padding: 5px;
  margin: 10px;
  background: azure;
  width:30%;
  text-align: center;
}

.todo {
  border: aqua 2px solid;
  border-radius: 10px;
  padding: 5px;
  margin: 10px;
  background: azure;

  text-align: center;
}

.user-info {
  border: aqua 2px solid;
  border-radius: 10px;
  padding: 5px;
  margin: 10px;
  width: 30%;
  background: azure;

  text-align: center;
}

.profile-image {
  width:50%;
  height: auto;
}
.create-todo-button {
  margin-bottom: 20px;
}
</style>
