Examui::Application.routes.draw do
  resources :pregunta

  resources :asignaturas

  devise_for :users

  root 'asignaturas#index'
end
