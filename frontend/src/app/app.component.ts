import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { ApiService, Category, Post, Token, User } from './api.service';

@Component({selector:'app-root',standalone:true,imports:[CommonModule,FormsModule],templateUrl:'./app.component.html'})
export class AppComponent implements OnInit {
  user:User|null=null; posts:Post[]=[]; categories:Category[]=[]; tokens:Token[]=[]; expanded=new Set<number>();
  username=''; password=''; title=''; body=''; category=''; search=''; tokenName='Assessment integration'; newToken=''; error=''; loading=true;
  constructor(public api:ApiService) {}
  ngOnInit(){ this.api.csrf().subscribe(()=>this.api.me().subscribe({next:u=>{this.user=u;this.loadTokens()},error:()=>{}})); this.load(); this.api.categories().subscribe(r=>this.categories=r.results); }
  message(e:unknown){ this.error=e instanceof HttpErrorResponse ? (e.error?.detail||'Something went wrong. Please try again.') : 'Something went wrong.'; }
  login(){ this.error=''; this.api.login(this.username,this.password).subscribe({next:u=>{this.user=u;this.password='';this.load();this.loadTokens()},error:e=>this.message(e)}); }
  logout(){ this.api.logout().subscribe(()=>{this.user=null;this.tokens=[];this.load()}); }
  load(){ this.loading=true; this.api.posts(this.category,this.search).subscribe({next:r=>{this.posts=Array.isArray(r)?r:r.results;this.loading=false},error:e=>{this.message(e);this.loading=false}}); }
  create(){ this.api.createPost(this.title,this.body).subscribe({next:()=>{this.title='';this.body='';this.load()},error:e=>this.message(e)}); }
  addComment(post:Post,input:HTMLInputElement){ if(!input.value.trim())return;this.api.comment(post.id,input.value).subscribe({next:()=>{input.value='';this.expanded.add(post.id);this.load()},error:e=>this.message(e)}); }
  toggleLike(post:Post){ this.api.like(post.id,post.liked_by_me).subscribe({next:()=>this.load(),error:e=>this.message(e)}); }
  moderate(post:Post,value:boolean){ this.api.moderate(post.id,value).subscribe({next:()=>this.load(),error:e=>this.message(e)}); }
  retry(post:Post){ this.api.retryAi(post.id).subscribe({next:()=>this.load(),error:e=>this.message(e)}); }
  loadTokens(){this.api.tokens().subscribe(r=>this.tokens=r.results)}
  createToken(){this.api.createToken(this.tokenName).subscribe({next:t=>{this.newToken=t.token||'';this.loadTokens()},error:e=>this.message(e)})}
  revoke(id:number){this.api.revokeToken(id).subscribe(()=>this.loadTokens())}
}

