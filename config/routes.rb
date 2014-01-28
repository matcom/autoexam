Examui::Application.routes.draw do
  resources :asignaturas

  devise_for :users

  root 'asignaturas#index'
end
