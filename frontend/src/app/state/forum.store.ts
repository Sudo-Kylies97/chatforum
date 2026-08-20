import { computed, inject, Injectable, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { finalize } from 'rxjs';
import { ApiService, Category, Post, Token, User } from '../api.service';

@Injectable({providedIn:'root'})
export class ForumStore {
  private readonly api = inject(ApiService);
  readonly user = signal<User|null>(null);
  readonly posts = signal<Post[]>([]);
  readonly categories = signal<Category[]>([]);
  readonly tokens = signal<Token[]>([]);
  readonly selectedCategory = signal('');
  readonly searchQuery = signal('');
  readonly loading = signal(false);
  readonly error = signal('');
  readonly newToken = signal('');
  readonly isAuthenticated = computed(() => this.user() !== null);
  readonly isModerator = computed(() => this.user()?.is_moderator === true);

  initialise(): void {
    this.api.csrf().subscribe({next:()=>this.restoreSession(), error:e=>this.handleError(e)});
    this.api.categories().subscribe({next:r=>this.categories.set(r.results), error:e=>this.handleError(e)});
    this.loadPosts();
  }
  restoreSession(): void {
    this.api.me().subscribe({next:u=>{this.user.set(u);this.loadTokens()},error:()=>this.user.set(null)});
  }
  login(username:string,password:string): void {
    this.clearError();
    this.api.login(username,password).subscribe({next:u=>{this.user.set(u);this.loadPosts();this.loadTokens()},error:e=>this.handleError(e)});
  }
  logout(): void {
    this.api.logout().subscribe({next:()=>{this.user.set(null);this.tokens.set([]);this.newToken.set('');this.loadPosts()},error:e=>this.handleError(e)});
  }
  loadPosts(): void {
    this.loading.set(true);
    this.api.posts(this.selectedCategory(),this.searchQuery()).pipe(finalize(()=>this.loading.set(false))).subscribe({next:r=>this.posts.set(Array.isArray(r)?r:r.results),error:e=>this.handleError(e)});
  }
  filter(category:string): void { this.selectedCategory.set(category);this.searchQuery.set('');this.loadPosts(); }
  search(query:string): void { this.searchQuery.set(query.trim());this.selectedCategory.set('');this.loadPosts(); }
  createPost(title:string,body:string,onComplete?:()=>void): void {
    this.api.createPost(title,body).subscribe({next:()=>{onComplete?.();this.loadPosts()},error:e=>this.handleError(e)});
  }
  addComment(postId:number,body:string,onComplete?:()=>void): void {
    this.api.comment(postId,body).subscribe({next:()=>{onComplete?.();this.loadPosts()},error:e=>this.handleError(e)});
  }
  toggleLike(post:Post): void { this.api.like(post.id,post.liked_by_me).subscribe({next:()=>this.loadPosts(),error:e=>this.handleError(e)}); }
  moderate(post:Post,value:boolean): void { this.api.moderate(post.id,value).subscribe({next:()=>this.loadPosts(),error:e=>this.handleError(e)}); }
  retryAi(postId:number): void { this.api.retryAi(postId).subscribe({next:()=>this.loadPosts(),error:e=>this.handleError(e)}); }
  loadTokens(): void { this.api.tokens().subscribe({next:r=>this.tokens.set(r.results),error:e=>this.handleError(e)}); }
  createToken(name:string): void { this.api.createToken(name).subscribe({next:t=>{this.newToken.set(t.token||'');this.loadTokens()},error:e=>this.handleError(e)}); }
  revokeToken(id:number): void { this.api.revokeToken(id).subscribe({next:()=>this.loadTokens(),error:e=>this.handleError(e)}); }
  clearError(): void { this.error.set(''); }
  private handleError(error:unknown): void {
    this.error.set(error instanceof HttpErrorResponse ? (error.error?.detail||'Something went wrong. Please try again.') : 'Something went wrong. Please try again.');
  }
}

