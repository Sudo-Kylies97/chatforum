import { ChangeDetectionStrategy, Component, inject, OnInit } from '@angular/core';
import { AppHeaderComponent } from './components/app-header/app-header.component';
import { FeedToolbarComponent } from './components/feed-toolbar/feed-toolbar.component';
import { PostCardComponent } from './components/post-card/post-card.component';
import { PostComposerComponent } from './components/post-composer/post-composer.component';
import { TokenManagerComponent } from './components/token-manager/token-manager.component';
import { ForumStore } from './state/forum.store';
@Component({selector:'app-root',standalone:true,changeDetection:ChangeDetectionStrategy.OnPush,imports:[AppHeaderComponent,FeedToolbarComponent,PostCardComponent,PostComposerComponent,TokenManagerComponent],templateUrl:'./app.component.html'})
export class AppComponent implements OnInit { readonly store=inject(ForumStore);ngOnInit():void{this.store.initialise();} }
