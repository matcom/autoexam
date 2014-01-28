require 'test_helper'

class ExamenControllerTest < ActionController::TestCase
  setup do
    @examan = examen(:one)
  end

  test "should get index" do
    get :index
    assert_response :success
    assert_not_nil assigns(:examen)
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should create examan" do
    assert_difference('Examan.count') do
      post :create, examan: { cantidad: @examan.cantidad, directorio: @examan.directorio, etiquetas: @examan.etiquetas, nombre: @examan.nombre }
    end

    assert_redirected_to examan_path(assigns(:examan))
  end

  test "should show examan" do
    get :show, id: @examan
    assert_response :success
  end

  test "should get edit" do
    get :edit, id: @examan
    assert_response :success
  end

  test "should update examan" do
    patch :update, id: @examan, examan: { cantidad: @examan.cantidad, directorio: @examan.directorio, etiquetas: @examan.etiquetas, nombre: @examan.nombre }
    assert_redirected_to examan_path(assigns(:examan))
  end

  test "should destroy examan" do
    assert_difference('Examan.count', -1) do
      delete :destroy, id: @examan
    end

    assert_redirected_to examen_path
  end
end
