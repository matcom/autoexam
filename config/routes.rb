Examui::Application.routes.draw do
  resources :listados

  resources :opcions

  resources :pregunta
  resources :asignaturas

  devise_for :users

  get 'nueva_pregunta/:id' => 'pregunta#nueva_pregunta', :as => :nueva_pregunta
  get 'nueva_opcion/:id' => 'opcions#nueva_opcion', :as => :nueva_opcion

  root 'asignaturas#index'
end
