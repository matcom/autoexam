Examui::Application.routes.draw do

  resources :examen
  resources :listados
  resources :opcions
  resources :pregunta
  resources :asignaturas

  devise_for :users

  get 'nueva_pregunta/:id' => 'pregunta#nueva_pregunta', :as => :nueva_pregunta
  get 'nueva_opcion/:id' => 'opcions#nueva_opcion', :as => :nueva_opcion
  get 'nuevo_examen/:id' => 'examen#new', :as => :nuevo_examen
  get 'clave/:id' => 'examen#clave', :as => :clave

  post 'update_clave' => 'examen#update_clave', :as => :update_clave

  root 'asignaturas#index'
end
