import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface User { id:number; username:string; is_moderator:boolean }
export interface Category { slug:string; name:string }
export interface Comment { id:number; author:User; body:string; created_at:string }
export interface Post { id:number; author:User; title:string; body:string; category:Category|null; is_misleading:boolean; created_at:string; comments:Comment[]; like_count:number; comment_count:number; liked_by_me:boolean; ai_status:string; ai_moderation_score:number|null; ai_moderation_rationale:string|null; ai_needs_review:boolean|null; vibe:string; vibe_status:string }
export interface Page<T> { count:number; next:string|null; previous:string|null; results:T[] }
export interface Token { id:number; name:string; prefix:string; created_at:string; revoked_at:string|null; token?:string }

@Injectable({providedIn:'root'})
export class ApiService {
  private base='/api/v1';
  constructor(private http:HttpClient) {}
  csrf(){ return this.http.get(`${this.base}/auth/csrf/`, {withCredentials:true}); }
  login(username:string,password:string){ return this.http.post<User>(`${this.base}/auth/login/`,{username,password},{withCredentials:true}); }
  logout(){ return this.http.post<void>(`${this.base}/auth/logout/`,{},{withCredentials:true}); }
  me(){ return this.http.get<User>(`${this.base}/auth/me/`,{withCredentials:true}); }
  posts(category=''):Observable<Page<Post>|Post[]> { const url=`${this.base}/posts/${category?`?category=${category}`:''}`; return this.http.get<Page<Post>|Post[]>(url,{withCredentials:true}); }
  createPost(title:string,body:string){ return this.http.post<Post>(`${this.base}/posts/`,{title,body},{withCredentials:true}); }
  comment(id:number,body:string){ return this.http.post<Comment>(`${this.base}/posts/${id}/comments/`,{body},{withCredentials:true}); }
  like(id:number, liked:boolean){ return liked?this.http.delete(`${this.base}/posts/${id}/like/`,{withCredentials:true}):this.http.post(`${this.base}/posts/${id}/like/`,{},{withCredentials:true}); }
  moderate(id:number,value:boolean){ return this.http.post<Post>(`${this.base}/posts/${id}/moderation/`,{is_misleading:value},{withCredentials:true}); }
  retryAi(id:number){ return this.http.post<Post>(`${this.base}/posts/${id}/retry_ai/`,{},{withCredentials:true}); }
  categories(){ return this.http.get<Page<Category>>(`${this.base}/categories/`); }
  tokens(){ return this.http.get<Page<Token>>(`${this.base}/tokens/`,{withCredentials:true}); }
  createToken(name:string){ return this.http.post<Token>(`${this.base}/tokens/`,{name},{withCredentials:true}); }
  revokeToken(id:number){ return this.http.delete(`${this.base}/tokens/${id}/`,{withCredentials:true}); }
}
