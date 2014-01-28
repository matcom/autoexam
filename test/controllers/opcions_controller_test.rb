require 'test_helper'

class OpcionsControllerTest < ActionController::TestCase
  setup do
    @opcion = opcions(:one)
  end

  test "should get index" do
    get :index
    assert_response :success
    assert_not_nil assigns(:opcions)
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should create opcion" do
    assert_difference('Opcion.count') do
      post :create, opcion: { preguntum_id: @opcion.preguntum_id, right: @opcion.right, titulo: @opcion.titulo }
    end

    assert_redirected_to opcion_path(assigns(:opcion))
  end

  test "should show opcion" do
    get :show, id: @opcion
    assert_response :success
  end

  test "should get edit" do
    get :edit, id: @opcion
    assert_response :success
  end

  test "should update opcion" do
    patch :update, id: @opcion, opcion: { preguntum_id: @opcion.preguntum_id, right: @opcion.right, titulo: @opcion.titulo }
    assert_redirected_to opcion_path(assigns(:opcion))
  end

  test "should destroy opcion" do
    assert_difference('Opcion.count', -1) do
      delete :destroy, id: @opcion
    end

    assert_redirected_to opcions_path
  end
end
