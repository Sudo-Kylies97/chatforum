import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient, withXsrfConfiguration } from '@angular/common/http';
import { AppComponent } from './app/app.component';
bootstrapApplication(AppComponent, {providers: [provideHttpClient(withXsrfConfiguration({cookieName: 'csrftoken', headerName: 'X-CSRFToken'}))]}).catch(console.error);

