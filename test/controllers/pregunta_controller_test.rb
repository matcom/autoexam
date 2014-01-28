require 'test_helper'

class PreguntaControllerTest < ActionController::TestCase
  setup do
    @preguntum = pregunta(:one)
  end

  test "should get index" do
    get :index
    assert_response :success
    assert_not_nil assigns(:pregunta)
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should create preguntum" do
    assert_difference('Preguntum.count') do
      post :create, preguntum: { asignatura_id: @preguntum.asignatura_id, etiquetas: @preguntum.etiquetas, titulo: @preguntum.titulo }
    end

    assert_redirected_to preguntum_path(assigns(:preguntum))
  end

  test "should show preguntum" do
    get :show, id: @preguntum
    assert_response :success
  end

  test "should get edit" do
    get :edit, id: @preguntum
    assert_response :success
  end

  test "should update preguntum" do
    patch :update, id: @preguntum, preguntum: { asignatura_id: @preguntum.asignatura_id, etiquetas: @preguntum.etiquetas, titulo: @preguntum.titulo }
    assert_redirected_to preguntum_path(assigns(:preguntum))
  end

  test "should destroy preguntum" do
    assert_difference('Preguntum.count', -1) do
      delete :destroy, id: @preguntum
    end

    assert_redirected_to pregunta_path
  end
end
