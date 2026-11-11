import type {User} from '../types/domain';
export function readUser():User|null{try{return JSON.parse(localStorage.getItem('mix-user')||'null')}catch{return null}}
export function saveSession(token:string,user:User){localStorage.setItem('mix-token',token);localStorage.setItem('mix-user',JSON.stringify(user))}
export function clearSession(){localStorage.removeItem('mix-token');localStorage.removeItem('mix-user')}
